import random

import yaml
import os
import logging
import math
import warnings
from collections.abc import Callable

from __init__ import root

yaml_logger = logging.getLogger(__name__)


class YamlReader:
    def __init__(self, filename: str):
        if not filename.endswith('.yaml'):
            raise ValueError('Wrong file type, must be `.yaml` extension')

        filepath = os.path.join(root, 'game_config', filename)
        yaml_logger.debug(f"reading {filename}")
        with open(filepath, 'r') as file:
            self.contents = yaml.safe_load(file)

        self.parse_special(self.contents)

    def parse_special(self,
                      cursor: dict):
        for attr, value in cursor.items():
            if isinstance(value, dict):
                self.parse_special(cursor=value)
            elif attr == 'decay_function':
                if "decay_factor" not in cursor.keys():
                    warnings.warn("Provided a decay function without a factor")
                cursor[attr] = self.str_to_decay_function(value, cursor["decay_factor"])

    @staticmethod
    def str_to_decay_function(fct_name: str,
                              factor: float,
                              ) -> Callable[[float, int], float]:
        """
        function signature : (epoch:int) → (resources left: float)
        """
        match fct_name:
            case 'linear':
                if 0 >= factor:
                    raise ValueError(f'Linear factor must be strictly positive')
                return lambda init_units, x: init_units - x*factor
            case 'geometric':
                if not 0 <= factor < 1:
                    raise ValueError(f'Geometric factor must be in [0, 1[')
                return lambda init_units, x: init_units * factor**x
            case 'exponential':
                if 0 >= factor:
                    raise ValueError(f'Exponential factor must be strictly positive')
                return lambda init_units, x: init_units * math.exp(-x / factor)
