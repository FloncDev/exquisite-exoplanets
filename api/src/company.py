import logging
from datetime import UTC, datetime

from src import Planet, RessourceCollector

company_logger = logging.getLogger(__name__)


class Company:
    """Class reprisenting a company in game."""

    def __init__(self, name: str, owner: str) -> None:
        self.name = name
        self.owner = owner
        self.join_date = datetime.now(tz=UTC)
        self.balance = 0
        self.planets = {}
        self.collectors = {}
        self.tier = 0
        self.planet_search = None
        self.collector_search = None

    @property
    def is_bankrupt(self) -> bool:
        """Returns True if balance <= 0."""
        return self.balance <= 0

    def explore(self,
                tier: int = None) -> "Planet":
        """generates a new planet for the company to harvest"""
        if not tier:
            tier = self.tier
        return Planet(tier=tier)

    def add_planet(self,
                   planet: "Planet") -> None:
        """adds the planet to the currently harvested planets"""
        self.planets[id(planet)] = planet

    def remove_planet(self,
                      planet: "Planet") -> None:
        """removes the planet from the currently harvested planets"""
        self.planets.pop(id(planet))

    def search_all_planets(self,
                           name: str):
        for p in self.planets.values():
            if p.name == name:
                yield p

    def search_planet(self,
                      name: str):
        if not self.planet_search:
            self.planet_search = self.search_all_planets(name)

        return next(self.planet_search, None)

    def add_collector(self,
                      collector: "ResourceCollector") -> None:
        """adds a collector to the available collectors"""
        self.collectors[id(collector)] = collector

    def remove_collector(self,
                         collector: "ResourceCollector") -> None:
        """removes the collector from the available collectors"""
        self.collectors.pop(id(collector))

    def search_all_collectors(self,
                              resource_name: str):
        for c in self.collectors.values():
            if c.resource.name == resource_name:
                yield c

    def search_collector(self,
                         resource_name: str):
        if not self.collector_search:
            self.collector_search = self.search_all_collectors(resource_name)

        return next(self.collector_search, None)


if __name__ == '__main__':
    import copy

    C = Company('Test', 'me')
    p = C.explore()
    C.add_planet(p)
    C.add_planet(copy.deepcopy(p))
    C.add_planet(C.explore())
    C.add_planet(C.explore())
    C.add_planet(C.explore())
    C.add_planet(copy.deepcopy(p))
    print(*C.planets.values(), sep='\n')

    target = p
    print(f'search `{target.name}`')

    while (search_result := C.search_planet(target.name)) is not None:
        print(search_result)
