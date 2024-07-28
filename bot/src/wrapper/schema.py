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
    RawPlanet,
    RawResource,
    RawResourceCollector,
    RawShopItem,
    RawUser,
    ShopIdPatchInput,
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

    company_id: int
    stock: int
    total_amount_spent: float
    item: Item

    @classmethod
    def from_dict(cls, src: RawInventoryItem) -> Self:
        """Convert json from http endpoint to InventoryItem object."""
        return cls(
            company_id=src["company_id"],
            stock=src["stock"],
            total_amount_spent=src["total_amount_spent"],
            item=Item.from_dict(src["item"]),
        )


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
            first_achieved=(AchievementRecord(**src["first_achieved"]) if src["first_achieved"] else None),
            latest_achieved=(AchievementRecord(**src["latest_achieved"]) if src["latest_achieved"] else None),
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
    planet: str
    current_networth: decimal.Decimal = field(default_factory=decimal.Decimal)
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
            created_date=datetime.datetime.fromisoformat(src["created"]),
            current_networth=decimal.Decimal(src["networth"] or 0),
            is_bankrupt=src["is_bankrupt"],
            planet=src["current_planet"],
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
        return {
            "available_quantity": self.quantity,
            "name": self.name,
            "price": self.price,
        }

    def to_modify(self) -> ShopIdPatchInput:
        """Convert this to the patch json to be send to API endpoint."""
        return {
            "item_id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
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


@dataclass
class Planet:
    """Model representing the details of a Planet to be returned to the User."""

    planet_id: str
    name: str
    description: str
    tier: int
    available_resources: list[str]

    @classmethod
    def from_dict(cls, src: RawPlanet) -> Self:
        """Convert json from http endpoint to Planet object."""
        return cls(**src)


@dataclass
class Resource:
    """Model representing the details of a Resource to be returned to the User."""

    resource_id: str
    name: str
    unit_price: float
    unit_xp: float
    min_tier: int
    found_on: list[str]

    @classmethod
    def from_dict(cls, src: RawResource) -> Self:
        """Convert json from http endpoint to Resource object."""
        return cls(**src)


@dataclass
class ResourceCollector:
    """Model representing the details of a Resource collector that can be returned to the User."""

    collector_id: str
    name: str
    init_price: float
    init_speed: float
    cost_of_use: float
    mineable_resources: list[str]

    @classmethod
    def from_dict(cls, src: RawResourceCollector) -> Self:
        """Convert json from http endpoint to Collector object."""
        return cls(**src)
