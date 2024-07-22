import re
from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel  # type: ignore[reportUnknownVariableType]


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
    owner_id: int = Field(nullable=False)

    @field_validator("name")
    @classmethod
    def valid_name(cls, s: str) -> str:
        """Check if the Company name is valid."""
        if re.search(r"^[a-zA-Z0-9\- .]+$", s) is None:
            msg = "Invalid Shop Item Name"
            raise ValueError(msg)
        return s

    # Relationships
    inventory: list["Inventory"] = Relationship(back_populates="company")


class CompanyCreate(SQLModel):
    """Model representing the data used to create a new Company."""

    name: str = Field(nullable=False)
    owner_id: int = Field(nullable=False)


class CompanyUpdate(SQLModel):
    """Model representing the data used to update a Company."""

    name: str | None = Field(default=None)

    @field_validator("name")
    @classmethod
    def valid_name(cls, s: str) -> str:
        """Check if the Company name is valid."""
        if re.search(r"^[a-zA-Z0-9\- .]+$", s) is None:
            msg = "Invalid Shop Item Name"
            raise ValueError(msg)
        return s


class CompanyPublic(SQLModel):
    """Model representing the data of a Company that can be returned."""

    id: int
    created: datetime
    name: str
    owner_id: int
    networth: float
    is_bankrupt: bool


###########################
# COMPANY INVENTORY SCHEMA
###########################


class Inventory(SQLModel, table=True):
    """Model representing a Company's inventory."""

    item_id: int = Field(foreign_key="shopitem.id", primary_key=True, nullable=False)
    company_id: int = Field(foreign_key="company.id", primary_key=True, nullable=False)
    stock: int = Field(ge=0, nullable=False)
    total_amount_spent: float = Field(ge=0, nullable=False)

    # Relationships
    item: "ShopItem" = Relationship(back_populates="inventories")
    company: "Company" = Relationship(back_populates="inventory")


class InventoryPublic(SQLModel):
    """Model representing the Inventory of a Company."""

    item: "ShopItemInventoryPublic"
    company_id: int
    stock: int
    total_amount_spent: float


#################
# USER SCHEMA
#################
class Experience(SQLModel):
    """A model representing a user's experience."""

    level: int = 0
    experience: int = 0


class User(SQLModel, table=True):
    """Model representing a User in the database."""

    user_id: int | None = Field(default=None, nullable=False, primary_key=True)
    registered: datetime | None = Field(nullable=False, default_factory=datetime.now)
    experience: int = Field(default=0, nullable=False)


class UserPublic(SQLModel):
    """Model representing a User that can be returned."""

    user_id: int
    experience: int


class UserCreatePublic(SQLModel):
    """Model representing the data used to create a new User."""

    id: int


class UserUpdateExperience(SQLModel):
    """Model representing the data used to update a user's experience."""

    new_experience: int


##############
# SHOP SCHEMA
##############
class ShopItem(SQLModel, table=True):
    """Model representing a Shop Item."""

    id: int = Field(nullable=False, primary_key=True)
    name: str = Field(nullable=False, max_length=32)
    price: float = Field(nullable=False, gt=0)
    available_quantity: int = Field(nullable=False, ge=0)
    is_disabled: bool = Field(nullable=False, default=False)

    # Relationships
    inventories: "Inventory" = Relationship(back_populates="item")


class ShopItemCreate(SQLModel):
    """Model representing a Shop Item that can be added to the Shop."""

    name: str = Field(max_length=32, min_length=1)
    price: float = Field(gt=0)
    available_quantity: int = Field(ge=0)

    @field_validator("name")
    @classmethod
    def valid_name(cls, s: str) -> str:
        """Check if the Shop Item name is valid."""
        if re.search(r"^[a-zA-Z0-9\- .]+$", s) is None:
            msg = "Invalid Shop Item Name"
            raise ValueError(msg)
        return s


class ShopItemUpdate(SQLModel):
    """Model representing the details of a Shop Item that can be updated."""

    item_id: int
    name: str | None = Field(default=None)
    quantity: int | None = Field(default=None, ge=0)
    price: float | None = Field(default=None, gt=0)
    is_disabled: bool | None = Field(default=None)

    @field_validator("name")
    @classmethod
    def valid_name(cls, s: str) -> str:
        """Check if the Shop Item name is valid."""
        if re.search(r"^[a-zA-Z0-9\- .]+$", s) is None:
            msg = "Invalid Shop Item Name"
            raise ValueError(msg)
        return s


class ShopItemPublic(SQLModel):
    """Model representing the details of the Shop Item that can be fetched."""

    id: int
    name: str
    price: float
    available_quantity: int
    is_disabled: bool


class ShopItemInventoryPublic(SQLModel):
    """Model representing the Shop Item information to be present in viewing a Company's inventory."""

    item_id: int
    name: str


class ShopItemPurchase(SQLModel):
    """Model representing the details of the Item being purchased."""

    company_id: int
    item_id: int
    purchase_quantity: int = Field(gt=0)
