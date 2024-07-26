import logging
import sys
from pathlib import Path

from src.company import company_logger
from src.planet import planet_logger
from src.resource import resource_logger
from src.resource_collector import collector_logger
from src.yaml_reader import yaml_logger

root = Path()  # application root
logs_dir = root.joinpath("logs")

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

debug_handler = logging.FileHandler(logs_dir.joinpath("debug.log"))
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)
cmd_handler = logging.StreamHandler(sys.stdout)
cmd_handler.setLevel(logging.INFO)
cmd_handler.setFormatter(formatter)

for logger in [
    company_logger,
    planet_logger,
    resource_logger,
    collector_logger,
    yaml_logger,
]:
    logger.addHandler(debug_handler)
    logger.addHandler(cmd_handler)
