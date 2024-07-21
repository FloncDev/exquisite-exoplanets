import datetime
import decimal
from dataclasses import dataclass, field
from typing import Self

from ._api_schema import CompanyGetIdOutput, RawShopItem


@dataclass
class Company:
    """A dataclass for basic company information from /company endpoint."""

    company_name: str
    owner_id: int
    created_date: datetime.datetime
    current_networth: decimal.Decimal | None = field(default_factory=decimal.Decimal)
    is_bankrupt: bool | None = False

    @classmethod
    def from_dict(cls, src: CompanyGetIdOutput) -> Self:
        """Convert json from http endpoint to Company object."""
        return cls(
            company_name=src["company_name"],
            owner_id=src["owner_id"],
            created_date=datetime.datetime.fromisoformat(src["created_date"]),
            current_networth=decimal.Decimal(src["current_networth"]),
            is_bankrupt=src["is_bankrupt"],
        )


@dataclass
class ShopItem:
    """A dataclass in represent of a specific item and its availability in the shop."""

    item_name: str
    item_price: float
    item_quantity: int

    @classmethod
    def from_dict(cls, src: RawShopItem) -> Self:
        """Convert json from http endpoint to ShopItem object."""
        return cls(**src)
