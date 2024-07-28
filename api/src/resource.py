import logging
import random
from typing import TYPE_CHECKING, Any

from .yaml_reader import YamlReader
from src import Planet, YamlReader
from src.resource_collector import ResourceCollector

if TYPE_CHECKING:
    from collections.abc import Callable

resource_logger = logging.getLogger(__name__)


class Resource:
    """Class representing an in game resource."""

    config: dict[str, Any] = YamlReader("Resource.yaml").contents

    def __init__(self, r_id: str, tier: int = 0) -> None:
        self._matconf = self.config[r_id]
        self.r_id = r_id
        self.name = self._matconf["name"]
        if tier < self._matconf["min_tier"]:
            error = f"{self._matconf['name']} can only appear on tier {self._matconf['min_tier']} or above"
            raise ValueError(error)

        self.tier = tier
        tier_upscaling = tier - self._matconf["min_tier"]

        self.unit_price = self._matconf["unit_price"]
        self.unit_xp = self._matconf["unit_xp"]

        # Having values of mu = 1 and sigma = 1/30 means you have a normal distribution centered on
        # 1 that can go as far as ]0.9, 1.1[
        self.init_units = (
            self._matconf["init_units"]
            * self._matconf["tier_units_upscale"] ** tier_upscaling
            * random.normalvariate(1, 1 / 30)
        )
        # the decay function has the signature
        # (init_units:int, epoch:int) -> units left rounded:int
        self.decay_function: Callable[[int, int], float] = YamlReader.str_to_decay_function(
            self._matconf["decay_function"], self._matconf["decay_factor"])
        self.epoch = 0

        self.balancing_delay = self._matconf["balancing_delay"]

        self.planet_parent = None
        self.collector_parent = None

    def set_planet_parent(self, planet: Planet | None) -> None:
        """Set the planet's parent."""
        self.planet_parent = planet

    def set_collector_parent(self, collector: ResourceCollector | None) -> None:
        """Set the collector's parent."""
        self.collector_parent = collector

    def get_units_left(self) -> float:
        """Get the amount of units left."""
        return self.decay_function(self.init_units, self.epoch)

    def get_units_collected(self) -> float:
        """Get the amount of units collected."""
        return self.init_units - self.get_units_left()

    def get_xp_collected(self) -> float:
        """Get the amount of xp collected."""
        return self.get_units_collected() * self.unit_xp

    def get_money_collected(self) -> float:
        """Get the amount of money collected."""
        return self.get_units_collected() * self.unit_price

    def collect(self, n: int = 1) -> float | None:
        """Collect resources then returns the amount of resources collected."""
        if n <= 0:
            error = "n must be strictly positive"
            raise ValueError(error)

        # find max epoch allowed
        for i in range(n, 0, -1):
            # check if the resource collection is possible
            if self.decay_function(self.init_units, self.epoch + i) >= 0:
                before_collection = self.get_units_collected()
                self.epoch += i
                return self.get_units_collected() - before_collection

        return None

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<name:{self.name}, tier:{self.tier}, units_left:{self.get_units_left()}>"
