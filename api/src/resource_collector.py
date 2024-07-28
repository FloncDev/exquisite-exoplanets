import datetime
import logging

from .resource import Resource
from .yaml_reader import YamlReader

collector_logger = logging.getLogger(__name__)


class ResourceCollector:
    """Class that represents any upgradable machine that can harvest materials
    Each instance is bound to one material only
    """

    config = YamlReader("ResourceCollector.yaml").contents
    epoch_definition = datetime.timedelta(hours=1)

    def __init__(self,
                 collector_id: str,
                 resource: Resource,
                 tier: int = 0) -> None:
        collector_conf = self.config[collector_id]
        self.name = collector_conf["name"]
        self.tier = tier
        self.auto_stop = float("inf")
        self.__init_price = collector_conf["init_price"]
        self.__init_speed = collector_conf["init_speed"]
        self.__upgrade_upscale = collector_conf["upgrade_upscale"]
        self.__upgrade_init_price = collector_conf["upgrade_init_price"]
        self.__upgrade_price_upscale = collector_conf["upgrade_price_upscale"]
        self.__cost_of_use = collector_conf["cost_of_use"]
        self.__cost_of_use_price_upscale = collector_conf["cost_of_use_price_upscale"]
        resources = collector_conf["resources"]
        if resource.r_id not in resources.keys():
            raise ValueError(f"Cannot extract {resource.name} with {self.name}")
        elif resource.tier > self.tier:
            raise ValueError(f"You need this extractor to be level {resource.tier}"
                             f"in order to extract {resource.name}")
        else:
            self.resource = resource
        self.__started_at: datetime.datetime = None
        self.__last_collected_at: datetime.datetime = None
        self.__epochs = 0

    def __get_relative_tier(self):
        return self.tier - self.resource.tier

    def get_speed(self) -> float:
        """Returns the harvesting speed"""
        return self.__init_speed * self.__upgrade_upscale ** self.__get_relative_tier()

    def get_next_upgrade_cost(self) -> float:
        """Returns the next harvesting speed upgrade price"""
        return self.__upgrade_init_price * self.__upgrade_price_upscale ** self.__get_relative_tier()

    def upgrade(self) -> None:
        """Makes the collector upgrade 1 tier"""
        self.tier += 1

    def get_cost(self, n: int = 1) -> float:
        """Returns the cost of use for `n` usage"""
        return (self.__cost_of_use * self.__cost_of_use_price_upscale ** self.__get_relative_tier()) * n

    def start(self) -> None:
        """Starts the resource harvesting"""
        start_time = datetime.datetime.now()
        self.__started_at = start_time
        self.__last_collected_at = start_time

    def stop(self) -> None:
        """Stops the resource harvesting"""
        self.__started_at = None

    def set_auto_stop(self,
                      stop_value: float) -> None:
        """Setter for the auto stop parameter"""
        if stop_value < 1:
            raise ValueError("auto stopping has to be greater or equal to 1")
        self.auto_stop = stop_value

    def collect(self) -> tuple[float, float, float]:
        """Collects resources then returns the amount collected and the cost of harvesting"""
        if not self.__last_collected_at:
            raise ValueError("collector has to be started before collecting")
        collection_time = datetime.datetime.now()
        epochs_since_last_collection = self.get_speed() * (
                collection_time - self.__last_collected_at) // self.epoch_definition
        epochs_since_last_collection = int(min(epochs_since_last_collection, self.auto_stop))
        self.__epochs += epochs_since_last_collection
        units_collected = self.resource.collect(epochs_since_last_collection)
        return units_collected, self.get_cost(epochs_since_last_collection), self.resource.unit_price * units_collected
