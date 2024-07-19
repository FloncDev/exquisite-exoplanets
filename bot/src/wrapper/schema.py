import datetime
import decimal
from dataclasses import dataclass, field
from typing import Self

from ._api_schema import CompanyPostIdOutput


@dataclass
class Company:
    """A dataclass for basic company information from /company endpoint."""

    company_name: str
    owner_id: int
    created_date: datetime.datetime
    current_networth: decimal.Decimal | None = field(default_factory=decimal.Decimal)
    is_bankrupt: bool | None = False

    @classmethod
    def from_dict(cls, src: CompanyPostIdOutput) -> Self:
        """Convert json from http endpoint to Company object."""
        return cls(
            company_name=src["company_name"],
            owner_id=src["owner_id"],
            created_date=datetime.datetime.fromisoformat(src["created_date"]),
            current_networth=decimal.Decimal(src["current_networth"]),
            is_bankrupt=src["is_bankrupt"],
        )
