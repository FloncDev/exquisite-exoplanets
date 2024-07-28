import logging
from collections.abc import Generator
from datetime import UTC, datetime

from src import Planet, ResourceCollector

company_logger = logging.getLogger(__name__)


class Company:
    """Class reprisenting a company in game."""

    def __init__(self, name: str, owner: str) -> None:
        self.name = name
        self.owner = owner
        self.join_date = datetime.now(tz=UTC)
        self.balance = 0
        self.planets: dict[int, Planet] = {}
        self.collectors: dict[int, ResourceCollector] = {}
        self.tier = 0
        self.planet_search = None
        self.collector_search = None

    @property
    def is_bankrupt(self) -> bool:
        """Returns True if balance <= 0."""
        return self.balance <= 0

    def explore(self, tier: int | None = None) -> Planet:
        """Generate a new planet for the company to harvest."""
        if not tier:
            tier = self.tier
        return Planet(tier=tier)

    def add_planet(self, planet: Planet) -> None:
        """Add the planet to the currently harvested planets."""
        self.planets[id(planet)] = planet

    def remove_planet(self, planet: Planet) -> None:
        """Remove the planet from the currently harvested planets."""
        self.planets.pop(id(planet))

    def search_all_planets(self, name: str) -> Generator[Planet]:
        """Search all planets for the given name."""
        for p in self.planets.values():
            if p.name == name:
                yield p

    def search_planet(self, name: str) -> Planet | None:
        """Search for a plent in self.planet_search."""
        if not self.planet_search:
            self.planet_search = self.search_all_planets(name)

        return next(self.planet_search, None)

    def add_collector(self, collector: ResourceCollector) -> None:
        """Add a collector to the available collectors."""
        self.collectors[id(collector)] = collector

    def remove_collector(self, collector: ResourceCollector) -> None:
        """Remove the collector from the available collectors."""
        self.collectors.pop(id(collector))

    def search_all_collectors(self, resource_name: str) -> Generator[ResourceCollector]:
        """Search all collectors for the given resource name."""
        for c in self.collectors.values():
            if c.resource is not None and c.resource.name == resource_name:
                yield c

    def search_collector(self, resource_name: str) -> ResourceCollector | None:
        """Search for a collector in self.collector_search."""
        if not self.collector_search:
            self.collector_search = self.search_all_collectors(resource_name)

        return next(self.collector_search, None)
