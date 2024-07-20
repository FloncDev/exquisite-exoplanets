from datetime import datetime

from sqlmodel import Field, SQLModel  # type: ignore[reportUnknownVariableType]


#################
# COMPANY SCHEMA
#################
class Company(SQLModel, table=True):
    """Model representing a Company in the database."""

    id: int | None = Field(primary_key=True, nullable=False, default=None)
    created: datetime | None = Field(nullable=False, default_factory=datetime.now)
    is_bankrupt: bool | None = Field(nullable=False, default=False)
    networth: float | None = Field(nullable=False, default=0)
    name: str = Field(nullable=False)
    owner_id: str = Field(nullable=False)


class CompanyCreate(SQLModel):
    """Model representing the data used to create a new Company."""

    name: str = Field(nullable=False)
    owner_id: str = Field(nullable=False)


class CompanyUpdate(SQLModel):
    """Model representing the data used to update a Company."""

    name: str | None = Field(default=None)


class CompanyPublic(SQLModel):
    """Model representing the data of a Company that can be returned."""

    id: int
    created: datetime
    name: str
    owner_id: str
    networth: float
    is_bankrupt: bool
