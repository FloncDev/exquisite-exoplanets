from YamlReader import YamlReader
import logging

resource_logger = logging.getLogger(__name__)

class Resource:
    __config:dict = YamlReader('Resource.yaml').contents
    def __init__(self):
        ...