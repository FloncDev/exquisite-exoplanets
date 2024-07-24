import logging
from typing import Any

from src import Resource, YamlReader

planet_logger = logging.getLogger(__name__)


class Planet:
    """Class reprisenting an in game planet."""

    all_resources: dict[str, Resource]
    _config: dict[str, Any] = YamlReader("Planet.yaml").contents

    def __init__(self, tier: int = 0) -> None:
        self.tier: int = tier
        self.resources: list[Resource] = []
        self.name: str = ""
        self.id: str = ""

    def spawn_resources(self) -> None:
        """Spawn resources on the planet."""

    @classmethod
    def spawn_planet(cls) -> "Planet":
        """Spawn a new planet."""
        return Planet()

    def generate_random_name(self) -> None:
        """Create a random name for the planet."""

    def generate_id(self) -> None:
        """Generate an id for the planet."""


if __name__ == "__main__":
    ...
