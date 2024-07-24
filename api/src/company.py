import logging
from datetime import UTC, datetime

company_logger = logging.getLogger(__name__)


class Company:
    """Class reprisenting a company in game."""

    def __init__(self, name: str, owner: str) -> None:
        self.name = name
        self.owner = owner
        self.join_date = datetime.now(tz=UTC)
        self.balance = 0
        self.planets = []
        self.inventory = []
        self.collectors = []

    @property
    def is_bankrupt(self) -> bool:
        """Returns True if balance <= 0."""
        return self.balance <= 0
