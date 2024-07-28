import re
from datetime import datetime

from pydantic import field_validator
from sqlmodel import (
    Field,  # type: ignore[reportUnknownVariableType]
    Relationship,
    SQLModel,
)


#################
# COMPANY SCHEMA
#################
class Company(SQLModel, table=True):
    """Model representing a Company in the database."""

    id: int | None = Field(primary_key=True, default=None)
    created: datetime = Field(nullable=False, default_factory=datetime.now)
    is_bankrupt: bool = Field(nullable=False, default=False)
    networth: float = Field(nullable=False, default=0)
    name: str = Field(nullable=False)
    owner_id: str = Field(nullable=False, foreign_key="user.user_id")
    current_planet: str = Field(foreign_key="planet.planet_id", nullable=False)

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
    achievements: list["EarnedAchievements"] = Relationship(back_populates="company")
    user: "User" = Relationship(back_populates="companies")
    planet: "PlanetModel" = Relationship(back_populates="companies_on")


class CompanyCreate(SQLModel):
    """Model representing the data used to create a new Company."""

    name: str = Field(nullable=False)
    owner_id: str = Field(nullable=False)


class CompanyUpdate(SQLModel):
    """Model representing the data used to update a Company."""

    name: str | None = Field(default=None)
    networth: float | None = Field(default=None)
    planet_name: str | None = Field(default=None)

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
    owner_id: str
    networth: float
    is_bankrupt: bool
    current_planet: str


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

    @staticmethod
    def level_from_experience(experience: int) -> int:
        """A function to calculate a level based on total experience."""  # noqa: D401
        return experience // 200


class User(SQLModel, table=True):
    """Model representing a User in the database."""

    user_id: str = Field(primary_key=True)
    registered: datetime | None = Field(nullable=False, default_factory=datetime.now)
    experience: int = Field(default=0, nullable=False)

    # Relationships
    companies: "Company" = Relationship(back_populates="user")


class UserExperienceReturn(SQLModel):
    """Model representing the data used set a user's experience."""

    level_up: bool
    new_level: int
    new_experience: int


class UserPublic(SQLModel):
    """Model representing a User that can be returned."""

    user_id: str
    experience: Experience


class UserCreatePublic(SQLModel):
    """Model representing the data used to create a new User."""

    id: str


class UserAddExperience(SQLModel):
    """Model representing the data used to add to a user's experience."""

    experience: int


class UserSetExperience(SQLModel):
    """Model representing the data used set a user's experience."""

    experience: int


##############
# SHOP SCHEMA
##############
class ShopItem(SQLModel, table=True):
    """Model representing a Shop Item."""

    id: int | None = Field(default=None, primary_key=True)
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

    company_id: str
    item_id: int
    purchase_quantity: int = Field(gt=0)


class ShopItemPurchasedPublic(SQLModel):
    """Model representing the details of the Shop Item that was purchased."""

    user_id: str
    company_id: int | None
    company_name: str
    item_id: int | None
    quantity: int
    new_balance: float


####################
# ACHIEVEMENT SCHEMA
####################
class Achievement(SQLModel, table=True):
    """Model representing the details of an Achievement."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)

    # Relationships
    companies_earned: list["EarnedAchievements"] = Relationship(back_populates="achievement")


class CompanyAchievementPublic(SQLModel):
    """Model representing the details of an Achievement achieved by a Company."""

    name: str
    owner_id: str
    date: datetime


class AchievementPublic(SQLModel):
    """Model representing the details of an Achievement seen when viewing an Achievement."""

    id: int
    name: str
    description: str
    companies_earned: int
    first_achieved: CompanyAchievementPublic | None
    latest_achieved: CompanyAchievementPublic | None


class AchievementsCompanyPublic(SQLModel):
    """Model representing the Achievements a Company has achieved."""

    class AchievementSingle(SQLModel):
        """Model representing the basic details of an Achievement."""

        id: int
        name: str
        description: str

    achievements: list[AchievementSingle] | None
    first_achievement: str
    latest_achievement: str


class EarnedAchievements(SQLModel, table=True):
    """Model representing a single Achievement earned by a Company."""

    achievement_id: int = Field(foreign_key="achievement.id", primary_key=True)
    company_id: int = Field(foreign_key="company.id", primary_key=True)
    achieved: datetime = Field(nullable=False, default_factory=datetime.now)

    # Relationships
    company: "Company" = Relationship(back_populates="achievements")
    achievement: "Achievement" = Relationship(back_populates="companies_earned")


######################
# GAME ENGINE SCHEMAS
######################
class PlanetModel(SQLModel, table=True):
    """Model representing a single Planet."""

    __tablename__ = "planet"

    id: int | None = Field(primary_key=True, default=None)
    planet_id: str = Field(nullable=False)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    tier: int = Field(nullable=False)

    # Relationships
    resources: list["PlanetResourcesModel"] = Relationship(back_populates="planet")
    companies_on: list["Company"] = Relationship(back_populates="planet")


class PlanetPublic(SQLModel):
    """Model representing the details of a Planet to be returned to a User."""

    planet_id: str
    name: str
    description: str
    tier: int
    available_resources: list[str]


class ResourceModel(SQLModel, table=True):
    """Model representing a single Resource."""

    __tablename__ = "resource"

    id: int | None = Field(primary_key=True, default=None)
    resource_id: str = Field(nullable=False)
    name: str = Field(nullable=False)
    min_tier: int = Field(nullable=False)
    unit_price: float = Field(nullable=False)
    unit_xp: float = Field(nullable=False)
    init_units: int = Field(nullable=False)
    tier_units_upscale: int = Field(nullable=False)
    decay_function: str = Field(nullable=False)
    decay_factor: float = Field(nullable=False)
    balancing_delay: float = Field(nullable=False)

    # Relationships
    on_planets: list["PlanetResourcesModel"] = Relationship(back_populates="resource")
    harvestable_by: "ResourceCollectorMineableResourcesModel" = Relationship(back_populates="resource")


class ResourcePublic(SQLModel):
    """Model representing the details of a Resource to be returned to the User."""

    resource_id: str
    name: str
    unit_price: float
    unit_xp: float
    min_tier: int
    found_on: list[str]


class PlanetResourcesModel(SQLModel, table=True):
    """Model representing all the Resources found on a Planet."""

    __tablename__ = "planet_resources"

    planet_id: int = Field(primary_key=True, foreign_key="planet.id")
    resource_id: int = Field(primary_key=True, foreign_key="resource.id")

    # Relationships
    planet: "PlanetModel" = Relationship(back_populates="resources")
    resource: "ResourceModel" = Relationship(back_populates="on_planets")


class ResourceCollectorModel(SQLModel, table=True):
    """Model representing a single Resource Collector."""

    __tablename__ = "resource_collector"

    id: int | None = Field(primary_key=True, default=None)
    collector_id: str = Field(nullable=False)
    name: str = Field(nullable=False)
    init_price: float = Field(nullable=False)
    init_speed: float = Field(nullable=False)
    upgrade_upscale: float = Field(nullable=False)
    upgrade_init_price: float = Field(nullable=False)
    upgrade_price_upscale: float = Field(nullable=False)
    cost_of_use: float = Field(nullable=False)
    cost_of_use_price_upscale: float = Field(nullable=False)

    # Relationships
    mineable_resources: list["ResourceCollectorMineableResourcesModel"] = Relationship(
        back_populates="resource_collector")


class ResourceCollectorPublic(SQLModel):
    """Model representing the details of a Resource collector that can be returned to the User"""

    collector_id: str
    name: str
    init_price: float
    init_speed: float
    cost_of_use: float
    mineable_resources: list[str]


class ResourceCollectorMineableResourcesModel(SQLModel, table=True):
    """Model representing the Resources that a Resource Collector can harvest."""

    __tablename__ = "collector_resources"

    resource_collector_id: int = Field(primary_key=True, foreign_key="resource_collector.id")
    resource_id: int = Field(primary_key=True, foreign_key="resource.id")

    # Relationships
    resource_collector: "ResourceCollectorModel" = Relationship(back_populates="mineable_resources")
    resource: "ResourceModel" = Relationship(back_populates="harvestable_by")
