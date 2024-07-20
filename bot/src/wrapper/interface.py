from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp

from ._communication import CompanyRawAPI, ShopRawAPI
from .error import DoNotExistError
from .schema import Company, ShopItem

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from ._api_schema import CompanyGetIdOutput, CompanyPatchIdInput, CompanyPostInput


class BaseAPI:
    """A BaseAPI with the required argument."""

    def __init__(self, address: str, token: str, *, parent: Interface) -> None:
        self.address = address
        self.token = token
        self.parent = parent


class CompanyAPI(BaseAPI):
    """Bundle of formatted API access to company endpoint."""

    async def create_company(self, user_id: int, company_name: str) -> Company:
        """Create an company for the user and return the Company."""
        src: CompanyPostInput = {"company_name": company_name, "owner_id": user_id}
        await CompanyRawAPI.create_company(self.address, self.token, src)
        return await self.get_company(user_id)

    async def get_company(self, user_id: int) -> Company:
        """Get the company from user id."""
        out: CompanyGetIdOutput = await CompanyRawAPI.get_company(self.address, self.token, user_id)
        return Company.from_dict(out)

    async def edit_company_name(self, company: Company | int, new_name: str) -> Company:
        """Edit the company name with the given user id."""
        if isinstance(company, Company):
            user_id: int = company.owner_id
        else:
            user_id: int = company
        src: CompanyPatchIdInput = {"company_name": new_name}
        await CompanyRawAPI.edit_company_name(self.address, self.token, user_id, src)
        return await self.get_company(user_id)

    async def delete_company(self, company: Company | int) -> None:
        """Delete the company with the given Company object or user ID."""
        if isinstance(company, Company):
            user_id: int = company.owner_id
        else:
            user_id: int = company
        await CompanyRawAPI.delete_company(self.address, self.token, user_id)

    async def list_companies(self, page: int = 1, limit: int = 10) -> list[Company]:
        """List companies from the database using paginator."""
        return [
            Company.from_dict(out)
            for out in await CompanyRawAPI.list_companies(self.address, self.token, page=page, limit=limit)
        ]

    async def iter_companies(self) -> AsyncGenerator[Company, None]:
        """Iterate through all company until there are no company left."""
        page = 1
        while True:
            try:
                for company in await self.list_companies(page=page):
                    yield company
                page += 1
            except DoNotExistError:
                return


class ShopAPI(BaseAPI):
    """Bundle of formatted API access to shop endpoint."""

    async def list_items(self) -> list[ShopItem]:
        """Return a list of shop items."""
        return [ShopItem.from_dict(out) for out in await ShopRawAPI.list_shop_items(self.address, self.token)]

    async def get_shop_item(self, item_id: int) -> ShopItem:
        """Get a specific shop item."""
        return ShopItem.from_dict(await ShopRawAPI.get_shop_item(self.address, self.token, item_id))

    async def purchase(self, item: int, company: Company | int, quantity: int) -> None:
        """Purchase item as the company."""
        if isinstance(company, Company):
            user_id: int = company.owner_id
        else:
            user_id: int = company
        await ShopRawAPI.purchase_shop_item(self.address, self.token, item, {"user_id": user_id, "quantity": quantity})


class Interface:
    """An API wrapper interface for the bot."""

    def __init__(self, address: str, token: str) -> None:
        """Initialize the interface with the address and API token."""
        self.address = address
        self.token = token
        self._session: aiohttp.ClientSession = aiohttp.ClientSession(base_url=address)

    @property
    def company(self) -> CompanyAPI:
        """Retrieve the Company API with the address and Token."""
        return CompanyAPI(self.address, self.token, parent=self)

    @property
    def shop(self) -> ShopAPI:
        """Retrieve the Shop API with the address and Token."""
        return ShopAPI(self.address, self.token, parent=self)

    @property
    def session(self) -> tuple[bool, aiohttp.ClientSession]:
        """Return the state of the session and the session."""
        return self._session.closed, self._session
