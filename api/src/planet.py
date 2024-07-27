import logging
from typing import Any
import random
import itertools

from api.src import Resource, YamlReader

planet_logger = logging.getLogger(__name__)


class Planet:
    """Class representing an in game planet."""

    _config: dict[str, Any] = YamlReader("Planet.yaml").contents
    _name_generator = None

    def __init__(self, tier: int = 0) -> None:
        self.tier: int = tier
        self.resources: list[Resource] = []
        self.spawn_resources()
        self.name: str = self.generate_random_name()
        self.id: str = ""

    def spawn_resources(self) -> None:
        """Spawn resources on the planet."""
        r_config = Resource.config
        for r_id in r_config.keys():
            match r_config[r_id]["min_tier"]:
                case _ if r_config[r_id]["min_tier"] < self.tier:  # if tier is inferior
                    tier_diff = self.tier - r_config[r_id]["min_tier"]
                    if random.random() < 1/(3*tier_diff):  # the chance of spawning is (1/3) * (1/tier difference)
                        self.resources.append(Resource(r_id, self.tier))
                case _ if r_config[r_id]["min_tier"] == self.tier:  # if tier is equal there is 100% chance of spawning
                    self.resources.append(Resource(r_id, self.tier))

    @classmethod
    def generate_random_name(cls) -> str:
        """Create a random name for the planet."""
        try:
            planet_name = next(cls._name_generator)
        except (StopIteration, TypeError):
            cls._name_generator = cls.name_generator()
            planet_name = cls.generate_random_name()
        return planet_name

    @classmethod
    def name_generator(cls) -> str:
        names = cls._config["names"]
        modifiers = cls._config["name_modifiers"]
        names_list = [f'{name} {modifier}' for name, modifier in itertools.product(names, modifiers)]
        random.shuffle(names_list)
        for name in names_list:
            yield name

    @staticmethod
    def generate_id(name: str) -> str:
        """Generate an id for the planet."""
        return f'{name[:2].upper()}{0:04}'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<name:{self.name},resources:{[str(e) for e in self.resources]}>"


if __name__ == "__main__":
    for _ in range(10):
        print(Planet(tier=3))
