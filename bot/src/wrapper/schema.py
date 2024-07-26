import datetime
import decimal
from dataclasses import dataclass, field
from typing import Self

from ._api_schema import (
    CompanyGetIdOutput,
    CompanyIdAchievementGetOutput,
    CompanyIdInventoryGetOutput,
    RawAchievement,
    RawAchievementRecord,
    RawBaseAchievement,
    RawExperience,
    RawInventoryItem,
    RawItem,
    RawShopItem,
    RawUser,
    ShopPostInput,
)


@dataclass
class Item:
    """Representation of an item."""

    id: int
    name: str

    @classmethod
    def from_dict(cls, src: RawItem) -> Self:
        """Convert json from http endpoint to Item object."""
        return cls(id=src["item_id"], name=src["name"])


@dataclass
class InventoryItem:
    """Representation of an item owned by a company."""

    stock: int
    total_amount_spent: float
    item: Item

    @classmethod
    def from_dict(cls, src: RawInventoryItem) -> Self:
        """Convert json from http endpoint to InventoryItem object."""
        return cls(stock=src["stock"], total_amount_spent=src["total_amount_spent"], item=Item.from_dict(src["item"]))


@dataclass
class AchievementRecord:
    """Representation of a user who held an achievement."""

    name: str
    owner_id: int
    date: str

    @classmethod
    def from_dict(cls, src: RawAchievementRecord) -> Self:
        """Convert json from http endpoint to AchievementRecord object."""
        return cls(**src)


@dataclass
class Achievement:
    """Representation of an achievement in game."""

    id: int
    name: str
    description: str
    companies_earned: int = -1
    first_achieved: AchievementRecord | None = None
    latest_achieved: AchievementRecord | None = None

    @classmethod
    def from_dict(cls, src: RawAchievement) -> Self:
        """Convert json from http endpoint to Achievement object."""
        return cls(
            id=src["id"],
            name=src["name"],
            description=src["description"],
            companies_earned=src.get("companies_earned", -1),
            first_achieved=AchievementRecord(**src["first_achieved"]) if src["first_achieved"] else None,
            latest_achieved=AchievementRecord(**src["latest_achieved"]) if src["latest_achieved"] else None,
        )

    @classmethod
    def from_partial_dict(cls, src: RawBaseAchievement) -> Self:
        """Convert json from http endpoint to Achievement object."""
        return cls(
            id=src["id"],
            name=src["name"],
            description=src["description"],
        )


@dataclass
class Company:
    """A dataclass for basic company information from /company endpoint."""

    id: int
    name: str
    owner_id: int
    created_date: datetime.datetime
    current_networth: decimal.Decimal | None = field(default_factory=decimal.Decimal)
    is_bankrupt: bool | None = False
    inventory: list[InventoryItem] | None = None
    achievements: list[Achievement] | None = None

    @classmethod
    def from_dict(cls, src: CompanyGetIdOutput) -> Self:
        """Convert json from http endpoint to Company object."""
        return cls(
            id=src["id"],
            name=src["name"],
            owner_id=int(src["owner_id"]),
            created_date=datetime.datetime.fromisoformat(src["created_date"]),
            current_networth=decimal.Decimal(src["current_networth"]),
            is_bankrupt=src["is_bankrupt"],
        )

    def set_inventory(self, src: CompanyIdInventoryGetOutput) -> Self:
        """Set the inventory of the company from data from HTTP request content."""
        self.inventory = [InventoryItem.from_dict(item) for item in src["inventory"]]
        return self

    def set_achievements(self, src: CompanyIdAchievementGetOutput) -> Self:
        """Set the achievements of the company from data from HTTP request content."""
        self.achievements = [Achievement.from_partial_dict(item) for item in src["achievements"]]
        return self


@dataclass
class ShopItem:
    """A dataclass in represent of a specific item and its availability in the shop."""

    id: int
    name: str
    price: float
    quantity: int
    is_disabled: bool

    @classmethod
    def from_dict(cls, src: RawShopItem) -> Self:
        """Convert json from http endpoint to ShopItem object."""
        return cls(
            id=src["id"],
            name=src["name"],
            price=src["price"],
            quantity=src["available_quantity"],
            is_disabled=src["is_disabled"],
        )

    def to_creation(self) -> ShopPostInput:
        """Convert a future Item to an item definition for item creation.

        :return: A dictionary of an item definition
        :raise ValueError: The item have already been created
        """
        if self.id == -1:
            msg = "This item have already been created with a given item id"
            raise ValueError(msg)
        return {"available_quantity": self.quantity, "name": self.name, "price": self.price}

    def to_modify(self) -> RawShopItem:
        """Convert this to the patch json to be send to API endpoint."""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "available_quantity": self.quantity,
            "is_disabled": self.is_disabled,
        }

    @classmethod
    def from_future_definition(cls, *, name: str, price: float, quantity: int) -> Self:
        """Create a future item to be created.

        :return: An incomplete object with `item_id = 1` for item definition
        """
        return cls(id=-1, name=name, price=price, quantity=quantity, is_disabled=False)


@dataclass
class Experience:
    """An object represent a experience and level."""

    level: int = 0
    experience: int = 0

    @classmethod
    def from_dict(cls, src: RawExperience) -> Self:
        """Convert json from http endpoint to Experience object."""
        return cls(**src)


@dataclass
class User:
    """An object to represent an user."""

    user_id: int
    experience: Experience = field(default_factory=Experience)

    @classmethod
    def from_dict(cls, src: RawUser) -> Self:
        """Convert json from http endpoint to User object."""
        return cls(user_id=src["user_id"], experience=Experience(**src["experience"]))
