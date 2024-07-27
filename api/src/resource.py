import logging
import random
from typing import TYPE_CHECKING, Any

from yaml_reader import YamlReader

if TYPE_CHECKING:
    from collections.abc import Callable

resource_logger = logging.getLogger(__name__)


class Resource:
    """Class representing an in game resource."""

    _config: dict[str, Any] = YamlReader("Resource.yaml").contents

    def __init__(self, mat_id: str, tier: int = 0) -> None:
        self._matconf = self._config[mat_id]
        self.name = self._matconf["name"]
        if tier < self._matconf["min_tier"]:
            raise ValueError(f"{self._matconf['name']} can only appear on tier {self._matconf['min_tier']} or above")

        self._tier = tier
        tier_upscaling = tier - self._matconf["min_tier"]

        self.unit_price = self._matconf["unit_price"]
        self.unit_xp = self._matconf["unit_xp"]

        # apparition probability is limited to 1
        self.apparition_probability = min(
            self._matconf["apparition_probability"] * self._matconf["tier_apparition_upscale"] ** tier_upscaling,
            1,
        )
        # mu = 1 and sigma = 1/30 means you have a normal distribution centered on 1 that can go as far as ]0.9, 1.1[
        self.init_units = (
                self._matconf["init_units"]
                * self._matconf["tier_units_upscale"] ** tier_upscaling
                * random.normalvariate(1, 1 / 30)
        )
        # the decay function has the signature
        # (init_units:int, epoch:int) -> units left rounded:int
        self.decay_function: Callable[[int, int], int] = self._matconf["decay_function"]
        self.epoch = 0

        self.balancing_delay = self._matconf["balancing_delay"]

    def get_units_left(self) -> float:
        """Get the amount of units left."""
        return self.decay_function(self.init_units, self.epoch)

    def get_units_collected(self) -> float:
        """Get the amount of units collected."""
        return self.init_units - self.get_units_left()

    def get_xp_collected(self) -> float:
        """Get the amount of units collected."""
        return self.epoch * self.unit_xp

    def collect(self, n: int = 1) -> float:
        """Collect resources."""
        if n <= 0:
            raise ValueError("n must be strictly positive")
        self.epoch += n
        return self.get_units_collected()

    def __str__(self) -> str:
        return f'<name:{self.name}, tier:{self._tier}, units_left:{self.get_units_left()}>'

