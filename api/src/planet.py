import itertools
import logging
import random
from collections.abc import Generator
from typing import Any

from src import Resource, YamlReader

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
        resource_instance: Resource
        for r_id in r_config:
            match r_config[r_id]["min_tier"]:
                case _ if r_config[r_id]["min_tier"] < self.tier:  # if tier is inferior
                    tier_diff = self.tier - r_config[r_id]["min_tier"]
                    if random.random() < 1 / (3 * tier_diff):  # noqa: S311
                        # the chance of spawning is (1/3) * (1/tier difference)
                        resource_instance = Resource(r_id, self.tier)
                        resource_instance.set_planet_parent(self)
                        self.resources.append(resource_instance)
                case _ if r_config[r_id]["min_tier"] == self.tier:  # if tier is equal there is 100% chance of spawning
                    resource_instance = Resource(r_id, self.tier)
                    resource_instance.set_planet_parent(self)
                    self.resources.append(resource_instance)
                case _:
                    pass

    @classmethod
    def generate_random_name(cls) -> str:
        """Create a random name for the planet."""
        if cls._name_generator is None:
            cls._name_generator = cls.name_generator()
        try:
            planet_name: str = next(cls._name_generator)
        except (StopIteration, TypeError):
            cls._name_generator = cls.name_generator()
            planet_name = cls.generate_random_name()
        return planet_name

    @classmethod
    def name_generator(cls) -> Generator[str, None, None]:
        """Generate random planet name."""
        names = cls._config["names"]
        modifiers = cls._config["name_modifiers"]
        names_list = [f"{name} {modifier}" for name, modifier in itertools.product(names, modifiers)]
        random.shuffle(names_list)
        yield from names_list

    @staticmethod
    def generate_id(name: str) -> str:
        """Generate an id for the planet."""
        return f"{name[:2].upper()}{0:04}"

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<name:{self.name},resources:{[str(e) for e in self.resources]}>"


if __name__ == "__main__":
    for _ in range(10):
        print(Planet(tier=3))
