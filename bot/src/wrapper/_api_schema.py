from typing import TypedDict


class CompanyPostInput(TypedDict):
    """JSON data for POST /conpany endpoint input."""

    name: str
    owner_id: str


class CompanyGetIdOutput(TypedDict):
    """JSON data for GET /conpany/{id} endpoint output."""

    id: int
    name: str
    owner_id: str
    created: str
    is_bankrupt: bool
    networth: float


class CompanyPatchIdInput(TypedDict):
    """JSON data for PUT /conpany/{id} endpoint input."""

    company_name: str


type BatchCompaniesOutput = list[CompanyGetIdOutput]
"""JSON data for GET /companies endpoint output"""


class RawItem(TypedDict):
    """A item object."""

    item_id: int
    name: str


class RawShopItem(TypedDict):
    """A item object from the shop."""

    id: int
    name: str
    price: float
    available_quantity: int
    is_disabled: bool


class ShopIdPatchInput(TypedDict):
    """A item object from the shop."""

    item_id: int
    name: str | None
    price: float | None
    quantity: int | None
    is_disabled: bool | None


class RawInventoryItem(TypedDict):
    """A representation of an item owned by the company."""

    company_id: int
    stock: int
    total_amount_spent: float
    item: RawItem


class CompanyIdInventoryGetOutput(TypedDict):
    """A representation of the inventories of the company."""

    company_id: int
    inventory: list[RawInventoryItem]


type ShopGetOutput = list[RawShopItem]
"""JSON data for GET /shop endpoint output."""

type ShopIdGetOutput = RawShopItem
"""JSON data for GET /shop/{id} endpoint output."""


class ShopBuyInput(TypedDict):
    """JSON data for PUT /shop/{id}/buy endpoint input."""

    company_id: str
    item_id: int
    purchase_quantity: int


class ShopBuyOutput(TypedDict):
    """JSON data for PUT /shop/{id}/buy endpoint output."""

    user_id: int
    item_id: int
    quantity: int
    new_balance: float


class RawExperience(TypedDict):
    """JSON data for a user experience info."""

    level: int
    experience: int


class RawUser(TypedDict):
    """JSON data for the user information."""

    user_id: int
    experience: RawExperience


type UserIdGetOutput = RawUser
"""JSON data for GET /user/{id} endpoint output."""


class UserIdExperiencePatchInput(TypedDict):
    new_experience: int


class UserIdExperiencePatchOutput(TypedDict):
    """JSON data for PATCH /user/{id}/experience endpoint output."""

    level_up: bool
    new_level: int
    new_experience: int


class UserIdExperiencePostInput(TypedDict):
    experience: int


type UserIdExperiencePostOutput = UserIdExperiencePatchOutput


class RawAchievementRecord(TypedDict):
    name: str
    owner_id: int
    date: str


class RawBaseAchievement(TypedDict):
    id: int
    name: str
    description: str


class RawAchievement(RawBaseAchievement):
    companies_earned: int
    first_achieved: RawAchievementRecord | None
    latest_achieved: RawAchievementRecord | None


class AchievementGetOutput(TypedDict):
    achievements: list[RawAchievement]


type AchievementIdGetOutput = RawAchievement


class ShopPostInput(TypedDict):
    name: str
    price: float
    available_quantity: int


class CompanyIdAchievementGetOutput(TypedDict):
    first_achievement: str
    latest_achievement: str
    achievements: list[RawBaseAchievement]
