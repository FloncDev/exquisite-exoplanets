from YamlReader import YamlReader
import logging
import random
from collections.abc import Callable

resource_logger = logging.getLogger(__name__)


class Resource:
    __config: dict = YamlReader('Resource.yaml').contents

    def __init__(self,
                 mat_id: str,
                 tier: int = 0):
        self.__matconf = self.__config[mat_id]
        self.__name = self.__matconf["name"]
        if tier < self.__matconf["min_tier"]:
            raise ValueError("Tier must be greater than minimum tier")
        else:
            self.__tier = tier
        self.__unit_price = self.__matconf["unit_price"]
        self.__unit_xp = self.__matconf["unit_xp"]
        self.__apparition_probability = min(self.__matconf["apparition_probability"]
                                            * self.__matconf["tier_apparition_upscale"] ** tier, 1)
        self.__init_units = (self.__matconf["init_units"] * self.__matconf["tier_units_upscale"] ** tier
                             * random.normalvariate(0.5, 1 / 60))
        self.__decay_function: Callable[[float, int], float] = self.__matconf["decay_function"]
        self.__epoch = 0

    def get_units_left(self):
        return self.__decay_function(self.__init_units, self.__epoch)

    def get_units_collected(self):
        return self.__init_units - self.get_units_left()

    def collect(self,
                n: int = 1):
        self.__epoch += n
        return self.get_units_collected()


