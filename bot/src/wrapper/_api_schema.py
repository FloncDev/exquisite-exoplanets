from typing import TypedDict


class CompanyPostInput(TypedDict):
    """JSON data for POST /conpany endpoint input."""

    company_name: str
    owner_id: int


class CompanyGetIdOutput(TypedDict):
    """JSON data for GET /conpany/{id} endpoint output."""

    company_name: str
    owner_id: int
    created_date: str
    is_bankrupt: bool
    current_networth: float


class CompanyPatchIdInput(TypedDict):
    """JSON data for PUT /conpany/{id} endpoint input."""

    company_name: str


type BatchCompaniesOutput = list[CompanyGetIdOutput]
"""JSON data for GET /companies endpoint output"""


class RawShopItem(TypedDict):
    """A item object from the shop."""

    item_id: int
    item_name: str
    item_price: float
    item_quantity: int


type ShopGetOutput = list[RawShopItem]
"""JSON data for GET /shop endpoint output."""

type ShopIdGetOutput = RawShopItem
"""JSON data for GET /shop/{id} endpoint output."""


class ShopBuyInput(TypedDict):
    """JSON data for PUT /shop/{id}/buy endpoint input."""

    user_id: int
    quantity: int


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
