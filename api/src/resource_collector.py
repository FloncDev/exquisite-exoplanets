import logging
import datetime

from src import YamlReader, Resource

collector_logger = logging.getLogger(__name__)


class ResourceCollector:
    """Class that represents any upgradable machine that can harvest materials"""

    config = YamlReader("ResourceCollector.yaml").contents
    epoch_definition = datetime.timedelta(hours=1)

    def __init__(self,
                 collector_id: str,
                 resource_id: str,
                 tier: int = 0) -> None:
        collector_conf = self.config[collector_id]
        self.name = collector_conf["name"]
        self.tier = tier
        self.init_price = collector_conf["init_price"]
        self.init_speed = collector_conf["init_speed"]
        self.speed_upgrade_upscale = collector_conf["speed_upgrade_upscale"]
        self.speed_upgrade_init_price = collector_conf["speed_upgrade_init_price"]
        self.speed_upgrade_price_upscale = collector_conf["speed_upgrade_price_upscale"]
        self.cost_of_use = collector_conf["cost_of_use"]
        self.cost_of_use_price_upscale = collector_conf["cost_of_use_price_upscale"]
        self.resources = collector_conf["resources"]
        if resource_id not in self.resources.keys():
            raise ValueError(f"Cannot extract {Resource.config[resource_id]['name']} with {self.name}")
        elif self.resources[resource_id] > tier:
            raise ValueError(f"You need this extractor to be level {self.resources[resource_id]} "
                             f"in order to extract {Resource.config[resource_id]['name']}")
        else:
            self.assignment = Resource(resource_id, tier)
        self.started_at: datetime.datetime = None
        self.last_collected_at: datetime.datetime = None
        self.epochs = 0

    def get_speed(self) -> float:
        """returns the harvesting speed"""
        return self.init_speed * self.speed_upgrade_upscale ** self.tier

    def get_next_speed_upgrade_cost(self) -> float:
        """returns the next harvesting speed upgrade price"""
        return self.speed_upgrade_init_price * self.speed_upgrade_price_upscale ** self.tier

    def upgrade(self) -> None:
        """makes the collector upgrade 1 tier"""
        self.tier += 1

    def get_cost(self, n: int = 1) -> float:
        """returns the cost of use for `n` usage"""
        return (self.cost_of_use * self.cost_of_use_price_upscale ** self.tier) * n

    def start(self) -> None:
        """starts the resource harvesting"""
        start_time = datetime.datetime.now()
        self.started_at = start_time
        self.last_collected_at = start_time

    def stop(self) -> None:
        """Stops the resource harvesting"""
        self.started_at = None

    def collect(self) -> tuple[float,float]:
        """collects resources then returns the amount collected and the cost of harvesting"""
        if not self.started_at:
            raise ValueError("collector has to be started before collecting")
        collection_time = datetime.datetime.now()
        epochs_since_last_collection = self.get_speed() * (collection_time - self.last_collected_at) // self.epoch_definition
        self.epochs += epochs_since_last_collection
        units_collected = self.assignment.collect(epochs_since_last_collection)
        return units_collected, self.get_cost(epochs_since_last_collection)


if __name__ == "__main__":
    ResourceCollector("MI00",  "UR00", 2)
