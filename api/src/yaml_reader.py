import logging
import math
import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

yaml_logger = logging.getLogger(__name__)
root = Path("../..")


class YamlReader:
    """Class to read YAML config files."""

    def __init__(self, filename: str) -> None:
        if not filename.endswith(".yaml"):
            error = "Wrong file type, must be `.yaml` extension"
            raise ValueError(error)

        filepath = root.joinpath("game_config", filename)
        yaml_logger.debug(f"reading {filename}")
        with filepath.open() as file:
            self.contents: dict[str, Any] = yaml.safe_load(file)

        self.parse_special(self.contents)

    def parse_special(self, cursor: dict[str, Any]) -> None:
        """Parse special YAML content."""
        for attr, value in cursor.items():
            if isinstance(value, dict):
                self.parse_special(
                    cursor=value  # pyright: ignore[reportUnknownArgumentType]
                )
            elif attr == "decay_function":
                if "decay_factor" not in cursor:
                    warnings.warn("Provided a decay function without a factor", stacklevel=2)
                cursor[attr] = self.str_to_decay_function(value, cursor["decay_factor"])

    @staticmethod
    def str_to_decay_function(
        fct_name: str,
        factor: float,
    ) -> Callable[[float, int], float]:
        """Match a string to a decay function.

        :param fct_name: Decay function name
        :returns: (epoch, int) -> (resources left: float)

        """
        match fct_name:
            case "linear":
                if factor <= 0:
                    error = "Linear factor must be strictly positive"
                    raise ValueError(error)

                return lambda init_units, x: init_units - x * factor

            case "geometric":
                if not 0 <= factor < 1:
                    error = "Geometric factor must be in [0, 1]"
                    raise ValueError(error)

                return lambda init_units, x: init_units * factor**x

            case "exponential":
                if factor <= 0:
                    error = "Exponential factor must be strictly positive"
                    raise ValueError(error)

                return lambda init_units, x: init_units * math.exp(-x / factor)

            case _:
                error = "Unknown fct_name"
                raise ValueError(error)
