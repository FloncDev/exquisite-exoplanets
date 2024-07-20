from enum import IntEnum

import aiohttp

from ._api_schema import (  # Company
    BatchCompaniesOutput,
    CompanyPatchIdInput,
    CompanyPostIdOutput,
    CompanyPostInput,
    RawShopItem,
    ShopBuyInput,
    ShopBuyOutput,
    ShopGetOutput,  # Shop
)
from .error import AlreadyExistError, DoNotExistError, UnknownNetworkError, UserError


class Status(IntEnum):
    """Store the used http status code from the api."""

    OK = 200
    OK_CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409


class CompanyRawAPI:
    """A bundle of API available to use for company endpoint."""

    @staticmethod
    async def create_company(address: str, token: str, src: CompanyPostInput) -> None:
        """Create a company with the given details through a direct HTTP request."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.post("/company", json=src) as resp,
        ):
            if resp.ok:
                return
            if resp.status == Status.CONFLICT:
                message = "This company name is already being used or The user already own a company"
                raise AlreadyExistError(message)
            message = (
                f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.create_company, Status received {resp.status}"
            )
            raise UnknownNetworkError(message)

    @staticmethod
    async def get_company(address: str, token: str, user_id: int) -> CompanyPostIdOutput:
        """Get the company details from user id of the discord user through a direct HTTP request."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.get(f"/company/{user_id}") as resp,
        ):
            if resp.ok:
                return await resp.json()
            if resp.status == Status.NOT_FOUND:
                message = "This user doesn't own a company"
                raise DoNotExistError(message)
            message = f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.get_company, Status received {resp.status}"
            raise UnknownNetworkError(message)

    @staticmethod
    async def edit_company_name(address: str, token: str, user_id: int, src: CompanyPatchIdInput) -> None:
        """Edit the company name with the user id of the discord user through a direct HTTP request."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.patch(f"/company/{user_id}", json=src) as resp,
        ):
            if resp.ok:
                return
            if resp.status == Status.NOT_FOUND:
                message = "This user doesn't own a company"
                raise DoNotExistError(message)
            message = (
                f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.edit_company_name, Status received {resp.status}"
            )
            raise UnknownNetworkError(message)

    @staticmethod
    async def delete_company(address: str, token: str, user_id: int) -> None:
        """Delete the company with the user id of the discord user through a direct HTTP request."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.delete(f"/company/{user_id}") as resp,
        ):
            if resp.ok:
                return
            if resp.status == Status.NOT_FOUND:
                message = "This user doesn't own a company"
                raise DoNotExistError(message)
            message = (
                f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.delete_company, Status received {resp.status}"
            )
            raise UnknownNetworkError(message)

    @staticmethod
    async def list_companies(address: str, token: str, page: int = 1, limit: int = 10) -> BatchCompaniesOutput:
        """Get a list of the registered Companies."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.get(
                "/companies", params={"Page": page, "Limit": limit}
            ) as resp,  # Require further clarification for the capitalization
        ):
            if resp.ok:
                return await resp.json()
            if resp.status == Status.NOT_FOUND:
                message = "No company found"
                raise DoNotExistError(message)
            message = (
                f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.list_companies, Status received {resp.status}"
            )
            raise UnknownNetworkError(message)


class ShopRawAPI:
    """A bundle of API available to use for company endpoint."""

    @staticmethod
    async def list_shop_items(address: str, token: str) -> ShopGetOutput:
        """Get a list of all item in the shop through a direct HTTP request."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.get("/shop") as resp,  # Require further clarification for the capitalization
        ):
            if resp.ok:
                return await resp.json()
            message = f"Undefined behaviour bot.src.wrapper.ShopRawAPI.list_shop_items, Status received {resp.status}"
            raise UnknownNetworkError(message)

    @staticmethod
    async def get_shop_item(address: str, token: str, item_id: int) -> RawShopItem:
        """Get a item by its id in the shop through a direct HTTP request."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.get(f"/shop/{item_id}") as resp,  # Require further clarification for the capitalization
        ):
            if resp.ok:
                return await resp.json()
            if resp.status == Status.NOT_FOUND:
                message = f"Item with item id: {item_id} not found"
                raise DoNotExistError(message)
            message = f"Undefined behaviour bot.src.wrapper.ShopRawAPI.get_shop_item, Status received {resp.status}"
            raise UnknownNetworkError(message)

    @staticmethod
    async def purchase_shop_item(address: str, token: str, item_id: int, src: ShopBuyInput) -> ShopBuyOutput:
        """Get a item by its id and quantity in the shop through a direct HTTP request."""
        async with (
            aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
            session.put(
                f"/shop/{item_id}/buy", json=src
            ) as resp,  # Require further clarification for the capitalization
        ):
            if resp.ok:
                return await resp.json()
            if resp.status == Status.UNAUTHORIZED:
                await CompanyRawAPI.get_company(address, token, src["user_id"])
                message = "Not enough balance"
                raise UserError(message)  # Should probably do further check on this
            if resp.status == Status.NOT_FOUND:
                message = f"Item with item id: {item_id} not found"
                raise DoNotExistError(message)
            message = (
                f"Undefined behaviour bot.src.wrapper.ShopRawAPI.purchase_shop_item, Status received {resp.status}"
            )
            raise UnknownNetworkError(message)
