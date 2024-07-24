import logging

from src import YamlReader

collector_logger = logging.getLogger(__name__)


class ResourceCollector:
    """Resource Collecter -- Please change to a better description."""

    _config = YamlReader("ResourceCollector.yaml").contents

    def __init__(self) -> None: ...
