import logging
import datetime

from src import YamlReader, Resource

collector_logger = logging.getLogger(__name__)


class ResourceCollector:
    """Class that represents any upgradable machine that can harvest materials
    Each instance is bound to one material only"""

    config = YamlReader("ResourceCollector.yaml").contents
    epoch_definition = datetime.timedelta(hours=1)

    def __init__(self,
                 collector_id: str,
                 tier: int = 0) -> None:
        collector_conf = self.config[collector_id]
        self.name = collector_conf["name"]
        self.tier = tier
        self.resource = None
        self.auto_stop = float('inf')
        self.__init_price = collector_conf["init_price"]
        self.__init_speed = collector_conf["init_speed"]
        self.__upgrade_upscale = collector_conf["upgrade_upscale"]
        self.__upgrade_init_price = collector_conf["upgrade_init_price"]
        self.__upgrade_price_upscale = collector_conf["upgrade_price_upscale"]
        self.__cost_of_use = collector_conf["cost_of_use"]
        self.__cost_of_use_price_upscale = collector_conf["cost_of_use_price_upscale"]
        self.__resources_allowed = self.config[collector_id]["resources"]
        self.started_at: datetime.datetime = None
        self.last_collected_at: datetime.datetime = None
        self.last_collection: tuple[float, float] = None
        self.epochs = 0

    def install(self,
                resource: "Resource") -> None:
        """attaches a collector to an instance of resource"""
        if resource.r_id not in self.__resources_allowed.keys():
            raise ValueError(f"Cannot extract {resource.name} with {self.name}")
        elif resource.tier > self.tier:
            raise ValueError(f"You need this extractor to be level {resource.tier}"
                             f"in order to extract {resource.name}")
        else:
            self.resource = resource
            self.resource.set_collector_parent(self)

    def uninstall(self) -> "Resource":
        """detaches the instance of resource"""
        self.reset()
        resource = self.resource
        resource.set_collector_parent(None)
        self.resource = None
        return resource

    def reset(self) -> None:
        """resets the parameters for a collector to allow it to be attributed to a new resource"""
        self.stop()
        self.collect()
        self.last_collection = None
        self.last_collected_at = None
        self.epochs = 0

    def __get_relative_tier(self):
        """gives the number of tiers between the collector's current tier and the harvested resource minimal tier"""
        if not self.resource:
            raise ValueError(f"no resource to count the relative tier from")
        return self.tier - self.__resources_allowed[self.resource.r_id]["min_tier"]

    def get_speed(self) -> float:
        """returns the harvesting speed"""
        return self.__init_speed * self.__upgrade_upscale ** self.__get_relative_tier()

    def get_next_upgrade_cost(self) -> float:
        """returns the next harvesting speed upgrade price"""
        return self.__upgrade_init_price * self.__upgrade_price_upscale ** self.__get_relative_tier()

    def upgrade(self) -> None:
        """makes the collector upgrade 1 tier"""
        self.tier += 1

    def get_cost(self, n: int = 1) -> float:
        """returns the cost of use for `n` usage"""
        return (self.__cost_of_use * self.__cost_of_use_price_upscale ** self.__get_relative_tier()) * n

    def start(self) -> None:
        """starts the resource harvesting"""
        if not self.resource:
            raise ValueError(f"The collector is not associated to a resource")
        start_time = datetime.datetime.now()
        self.started_at = start_time
        self.last_collected_at = start_time

    def stop(self) -> None:
        """Stops the resource harvesting"""
        self.started_at = None
        self.collect()

    def set_auto_stop(self,
                      stop_value: float) -> None:
        """setter for the auto stop parameter"""
        if stop_value < 1:
            raise ValueError(f"auto stopping has to be greater or equal to 1")
        self.auto_stop = stop_value

    def collect(self) -> tuple[float, float]:
        """collects resources then returns the amount collected and the cost of harvesting"""
        if not self.last_collected_at:
            raise ValueError("collector has to be started before collecting")
        collection_time = datetime.datetime.now()
        epochs_since_last_collection = self.get_speed() * (collection_time - self.last_collected_at) // self.epoch_definition
        epochs_since_last_collection = int(min(epochs_since_last_collection, self.auto_stop))
        self.epochs += epochs_since_last_collection
        units_collected = self.resource.collect(epochs_since_last_collection)
        self.last_collection = units_collected, self.get_cost(epochs_since_last_collection)
        return self.last_collection

    def last_collection_detail(self):
        details = dict(
            units_collected=self.last_collection[0],
            units_left=self.resource.get_units_left(),
            cost=self.last_collection[1],
            raw_worth=self.last_collection[0] * self.resource.unit_price,
            net_worth=(self.last_collection[0] * self.resource.unit_price) - self.last_collection[1],
            xp_earned=self.last_collection[0] * self.resource.unit_xp
        )
        return details

    def total_collection_detail(self):
        details = dict(
            units_collected=self.resource.get_units_collected(),
            units_left=self.resource.get_units_left(),
            cost=self.__cost_of_use * self.epochs,
            raw_worth=self.resource.get_units_collected() * self.resource.unit_price,
            net_worth=(self.resource.get_units_collected() * self.resource.unit_price) - (self.__cost_of_use * self.epochs),
            xp_earned=self.resource.get_units_collected() * self.resource.unit_xp
        )
        return details

    def __repr__(self):
        return self.__str__()

    def __str__(self) -> str:
        return f'<name:{self.name}, tier:{self.tier}, resource:{self.resource}>'
