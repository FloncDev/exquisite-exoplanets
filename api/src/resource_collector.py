import logging
from datetime import UTC, datetime, timedelta

from src import Resource

from .yaml_reader import YamlReader

collector_logger = logging.getLogger(__name__)


class ResourceCollector:
    """Class that represents any upgradable machine that can harvest materials.

    Each instance is bound to one material only
    """

    config = YamlReader("ResourceCollector.yaml").contents
    epoch_definition = timedelta(hours=1)

    def __init__(self, collector_id: str, tier: int = 0) -> None:
        collector_conf = self.config[collector_id]
        self.name = collector_conf["name"]
        self.tier = tier
        self.resource = None
        self.auto_stop = float("inf")
        self._init_price = collector_conf["init_price"]
        self._init_speed = collector_conf["init_speed"]
        self._upgrade_upscale = collector_conf["upgrade_upscale"]
        self._upgrade_init_price = collector_conf["upgrade_init_price"]
        self._upgrade_price_upscale = collector_conf["upgrade_price_upscale"]
        self._cost_of_use = collector_conf["cost_of_use"]
        self._cost_of_use_price_upscale = collector_conf["cost_of_use_price_upscale"]
        self._resources_allowed = self.config[collector_id]["resources"]
        self.started_at: datetime | None = None
        self.last_collected_at: datetime | None = None
        self.last_collection: tuple[float, float] | None = None
        self.epochs = 0

    def install(self, resource: "Resource") -> None:
        """Attaches a collector to an instance of resource."""
        if resource.r_id not in self._resources_allowed:
            error = f"Cannot extract {resource.name} with {self.name}"
            raise ValueError(error)

        if resource.tier > self.tier:
            error = f"You need this extractor to be level {resource.tier}" f"in order to extract {resource.name}"
            raise ValueError(error)

        self.resource = resource
        self.resource.set_collector_parent(self)

    def uninstall(self) -> Resource | None:
        """Detaches the instance of resource."""
        self.reset()
        resource = self.resource
        if resource is not None:
            resource.set_collector_parent(None)
        self.resource = None
        return resource

    def reset(self) -> None:
        """Reset the parameters for a collector to allow it to be attributed to a new resource."""
        self.stop()
        self.collect()
        self.last_collection = None
        self.last_collected_at = None
        self.epochs = 0

    def _get_relative_tier(self) -> int:
        """Give the number of tiers between the collector's current tier and the harvested resource minimal tier."""
        if not self.resource:
            error = "no resource to count the relative tier from"
            raise ValueError(error)
        return self.tier - self._resources_allowed[self.resource.r_id]["min_tier"]

    def get_speed(self) -> float:
        """Return the harvesting speed."""
        return self._init_speed * self._upgrade_upscale ** self._get_relative_tier()

    def get_next_upgrade_cost(self) -> float:
        """Return the next harvesting speed upgrade price."""
        return self._upgrade_init_price * self._upgrade_price_upscale ** self._get_relative_tier()

    def upgrade(self) -> None:
        """Make the collector upgrade 1 tier."""
        self.tier += 1

    def get_cost(self, n: int = 1) -> float:
        """Return the cost of use for `n` usage."""
        return (self._cost_of_use * self._cost_of_use_price_upscale ** self._get_relative_tier()) * n

    def start(self) -> None:
        """Rtart the resource harvesting."""
        if not self.resource:
            error = "The collector is not associated to a resource"
            raise ValueError(error)
        start_time = datetime.now(tz=UTC)
        self.started_at = start_time
        self.last_collected_at = start_time

    def stop(self) -> None:
        """Stop the resource harvesting."""
        self.started_at = None
        self.collect()

    def set_auto_stop(self, stop_value: float) -> None:
        """Setter for the auto stop parameter."""
        if stop_value < 1:
            error = "auto stopping has to be greater or equal to 1"
            raise ValueError(error)
        self.auto_stop = stop_value

    def collect(self) -> tuple[float, float]:
        """Collect resources then returns the amount collected and the cost of harvesting."""
        if not self.last_collected_at:
            error = "collector has to be started before collecting"
            raise ValueError(error)

        if self.resource is None:
            error = "Resource is None"
            raise ValueError(error)

        collection_time = datetime.now(tz=UTC)
        epochs_since_last_collection = (
            self.get_speed() * (collection_time - self.last_collected_at) // self.epoch_definition
        )
        epochs_since_last_collection = int(min(epochs_since_last_collection, self.auto_stop))
        self.epochs += epochs_since_last_collection
        units_collected = self.resource.collect(epochs_since_last_collection) or 0.0
        self.last_collection = units_collected, self.get_cost(epochs_since_last_collection)
        return self.last_collection

    def last_collection_detail(self) -> dict[str, float]:
        """Return details of last collection."""
        if self.last_collection is None:
            error = "last_collection is None"
            raise ValueError(error)

        if self.resource is None:
            error = "self.resource is None"
            raise ValueError(error)

        return {
            "units_collected": self.last_collection[0],
            "units_left": self.resource.get_units_left(),
            "cost": self.last_collection[1],
            "raw_worth": self.last_collection[0] * self.resource.unit_price,
            "net_worth": (self.last_collection[0] * self.resource.unit_price) - self.last_collection[1],
            "xp_earned": self.last_collection[0] * self.resource.unit_xp,
        }

    def total_collection_detail(self) -> dict[str, float]:
        """Return details of the colletion totals."""
        if self.resource is None:
            error = "self.resource is None"
            raise ValueError(error)

        return {
            "units_collected": self.resource.get_units_collected(),
            "units_left": self.resource.get_units_left(),
            "cost": self._cost_of_use * self.epochs,
            "raw_worth": self.resource.get_units_collected() * self.resource.unit_price,
            "net_worth": (self.resource.get_units_collected() * self.resource.unit_price)
            - (self._cost_of_use * self.epochs),
            "xp_earned": self.resource.get_units_collected() * self.resource.unit_xp,
        }

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<name:{self.name}, tier:{self.tier}, resource:{self.resource}>"
