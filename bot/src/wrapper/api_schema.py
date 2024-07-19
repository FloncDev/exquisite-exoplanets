from typing import TypedDict, TypeAlias


class CompanyPostInput(TypedDict):
    company_name: str
    owner_id: int


class CompanyPostOutput(TypedDict):
    company_name: str
    owner_id: int
    created_date: str


class CompanyPostIdOutput(CompanyPostOutput):
    is_bankrupt: bool
    current_networth: float


class CompanyPatchIdInput(TypedDict):
    company_name: str


class ShopItem(TypedDict):
    item_name: str
    item_price: float
    item_quantity: int


ShopGetOutput: TypeAlias = list[ShopItem]

ShopIdGetOutput: TypeAlias = ShopItem


class ShopBuyInput(TypedDict):
    user_id: int
    quantity: int


class ShopBuyOutput(TypedDict):
    user_id: int
    item_id: int
    quantity: int
    new_balance: float
