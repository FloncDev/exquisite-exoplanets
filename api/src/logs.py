import logging
import os
import sys
from Company import company_logger
from Planet import planet_logger
from Resource import resource_logger
from ResourceCollector import collector_logger
from YamlReader import yaml_logger

root='' # application root
logs_dir = os.path.join(root, 'logs')

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

debug_handler = logging.FileHandler(os.path.join(logs_dir, 'debug.log'))
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(formatter)
cmd_handler = logging.StreamHandler(sys.stdout)
cmd_handler.setLevel(logging.INFO)
cmd_handler.setFormatter(formatter)

for logger in [company_logger, planet_logger, resource_logger, collector_logger, yaml_logger]:
    logger.addHandler(debug_handler)
    logger.addHandler(cmd_handler)
