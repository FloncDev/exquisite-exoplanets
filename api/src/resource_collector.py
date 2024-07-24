from Resource import Resource
from YamlReader import YamlReader
import logging

collector_logger = logging.getLogger(__name__)

class ResourceCollector:
    __config:dict = YamlReader('ResourceCollector.yaml').contents
    def __init__(self):
        ...