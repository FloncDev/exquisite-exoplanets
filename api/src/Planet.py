import random
import logging
from Resource import Resource
from YamlReader import YamlReader

planet_logger = logging.getLogger(__name__)


class Planet:
    __all_resources: dict[str:Resource]
    __config: dict = YamlReader('Planet.yaml').contents

    def __init__(self, tier:int = 0):
        self.__tier: int = tier
        self.__resources: list[Resource] = []
        self.__name: str = ''
        self.__id: str = ''

    def spawn_resources(self):
        ...

    @classmethod
    def spawn_planet(cls):
        ...

    def generate_random_name(self):
        ...

    def generate_id(self):
        ...


if __name__ == '__main__':
    ...
