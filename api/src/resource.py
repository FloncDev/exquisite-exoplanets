import logging
import random
from typing import TYPE_CHECKING, Any

from src import YamlReader

if TYPE_CHECKING:
    from collections.abc import Callable

resource_logger = logging.getLogger(__name__)


class Resource:
    """Class reprisenting an in game resource."""

    _config: dict[str, Any] = YamlReader("Resource.yaml").contents

    def __init__(self, mat_id: str, tier: int = 0) -> None:
        self._matconf = self._config[mat_id]
        self.name = self._matconf["name"]
        if tier < self._matconf["min_tier"]:
            error = "Tier must be greater than minimum tier"
            raise ValueError(error)

        self._tier = tier
        self.unit_price = self._matconf["unit_price"]
        self.unit_xp = self._matconf["unit_xp"]
        self.apparition_probability = min(
            self._matconf["apparition_probability"] * self._matconf["tier_apparition_upscale"] ** tier,
            1,
        )
        self.init_units = (
            self._matconf["init_units"]
            * self._matconf["tier_units_upscale"] ** tier
            * random.normalvariate(0.5, 1 / 60)
        )
        self.decay_function: Callable[[float, int], float] = self._matconf["decay_function"]
        self.epoch = 0

    def get_units_left(self) -> float:
        """Get the amount of units left."""
        return self.decay_function(self.init_units, self.epoch)

    def get_units_collected(self) -> float:
        """Get the amount of units collected."""
        return self.init_units - self.get_units_left()

    def collect(self, n: int = 1) -> float:
        """Collect resources."""
        self.epoch += n
        return self.get_units_collected()
