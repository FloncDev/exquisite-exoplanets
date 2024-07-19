import datetime
import decimal
from dataclasses import dataclass, field
from typing import Optional, Self, TypeGuard

from .api_schema import CompanyPostOutput, CompanyPostIdOutput


def is_post_id_output(src: CompanyPostOutput) -> TypeGuard[CompanyPostIdOutput]:
    return "current_networth" in dir(src) and "is_bankrupt" in dir(src)


@dataclass
class Company:
    company_name: str
    owner_id: int
    created_date: datetime.datetime
    current_networth: Optional[decimal.Decimal] = field(default_factory=decimal.Decimal)
    is_bankrupt: Optional[bool] = False

    @classmethod
    def from_dict(cls, src: CompanyPostOutput) -> Self:
        if is_post_id_output(src):
            return cls(
                company_name=src["company_name"],
                owner_id=src["owner_id"],
                created_date=datetime.datetime.fromisoformat(src["created_date"]),
                current_networth=decimal.Decimal(src["current_networth"]),
                is_bankrupt=src["is_bankrupt"],
            )
        else:
            return cls(
                company_name=src["company_name"],
                owner_id=src["owner_id"],
                created_date=datetime.datetime.fromisoformat(src["created_date"]),
            )
