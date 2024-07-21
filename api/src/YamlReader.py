import yaml
import os
import logging
from collections.abc import Callable

from __init__ import root

yaml_logger = logging.getLogger(__name__)

class YamlReader:
    def __init__(self, filename:str):
        if not filename.endswith('.yaml'):
            raise ValueError('Wrong file type, must be `.yaml` extension')

        filepath = os.path.join(root, 'game_config', filename)
        yaml_logger.debug(f"reading {filename}")
        with open(filepath, 'r') as file:
            self.contents = yaml.safe_load(file)

    def parse_special(self, cursor:object):
        if isinstance(cursor, dict):
            for attr, value in cursor.items():
                if attr=='density_decay_function':
                    cursor[attr]
                self.parse_special(cursor=value)

    @staticmethod
    def str_to_decay_function(fct_name: str,
                              factor: float
                              )-> Callable[[float], ]:
        """
        function signature : (factor:float) → (amount reduced: float)
        """
        match fct_name:
            case 'linear':
                ...
            case 'exponential':
                ...
            case 'geometric':
                ...
            case 'random':
                ...