from datetime import datetime

from sqlmodel import Field, SQLModel  # type: ignore


#################
# COMPANY SCHEMA
#################
class Company(SQLModel, table=True):
    id: int | None = Field(primary_key=True, nullable=False, default=None)
    created: datetime | None = Field(nullable=False, default_factory=datetime.now)
    is_bankrupt: bool | None = Field(nullable=False, default=False)
    networth: float | None = Field(nullable=False, default=0)
    name: str = Field(nullable=False)
    owner: str = Field(nullable=False)


class CompanyCreate(SQLModel):
    name: str = Field(nullable=False)
    owner: str = Field(nullable=False)


class CompanyPublic(SQLModel):
    id: int
    created: datetime
    name: str
    owner: str
    networth: float
    is_bankrupt: bool
