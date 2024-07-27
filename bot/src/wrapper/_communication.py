from collections.abc import Callable, Coroutine
from enum import IntEnum
from typing import Literal

import aiohttp

from ._api_schema import (  # Company
    AchievementGetOutput,  # Achievement
    AchievementIdGetOutput,
    BatchCompaniesOutput,
    CompanyGetIdOutput,
    CompanyIdAchievementGetOutput,
    CompanyIdInventoryGetOutput,
    CompanyPatchIdInput,
    CompanyPostInput,
    RawShopItem,  # Shop
    ShopBuyInput,
    ShopBuyOutput,
    ShopGetOutput,
    ShopIdPatchInput,
    ShopPostInput,
    UserIdExperiencePatchInput,  # User
    UserIdExperiencePatchOutput,
    UserIdExperiencePostInput,
    UserIdExperiencePostOutput,
    UserIdGetOutput,
)
from .error import AlreadyExistError, DoesNotExistError, UnknownNetworkError, UserError


async def make_request[T](
    session: aiohttp.ClientSession,
    func: Callable[[aiohttp.ClientSession], Coroutine[None, None, T]],
) -> T:
    if session.closed:
        async with session:
            return await func(session)
    return await func(session)


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
    async def create_company(session: aiohttp.ClientSession, src: CompanyPostInput) -> CompanyGetIdOutput:
        """Create a company with the given details through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> CompanyGetIdOutput:
            async with (
                session.post("/company", json=src) as resp,
            ):
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.CONFLICT:
                    message = "This company name is already being used or The user already own a company"
                    raise AlreadyExistError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.create_company, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def get_company(session: aiohttp.ClientSession, user_id: int) -> CompanyGetIdOutput:
        """Get the company details from user id of the discord user through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> CompanyGetIdOutput:
            async with (
                session.get(f"/company/{user_id}") as resp,
            ):
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = "This user doesn't own a company"
                    raise DoesNotExistError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.get_company, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def edit_company_name(session: aiohttp.ClientSession, user_id: int, src: CompanyPatchIdInput) -> None:
        """Edit the company name with the user id of the discord user through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> None:
            async with (
                session.patch(f"/company/{user_id}", json=src) as resp,
            ):
                if resp.ok:
                    return
                if resp.status == Status.NOT_FOUND:
                    message = "This user doesn't own a company"
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.CompanyRawAPI.edit_company_name, "
                    f"Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def delete_company(session: aiohttp.ClientSession, user_id: int) -> None:
        """Delete the company with the user id of the discord user through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> None:
            async with (
                session.delete(f"/company/{user_id}") as resp,
            ):
                if resp.ok:
                    return
                if resp.status == Status.NOT_FOUND:
                    message = "This user doesn't own a company"
                    raise DoesNotExistError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.delete_company, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def list_companies(
        session: aiohttp.ClientSession, page: int = 1, limit: int = 10, *, ascending: bool = False
    ) -> BatchCompaniesOutput:
        """Get a list of the registered Companies."""

        async def caller(session: aiohttp.ClientSession) -> BatchCompaniesOutput:
            async with (
                session.get("/companies", params={"page": page, "limit": limit, "ascending": str(ascending)}) as resp,
            ):
                if resp.ok:
                    return (await resp.json())["companies"]
                if resp.status == Status.NOT_FOUND:
                    message = "No company found"
                    raise DoesNotExistError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.CompanyRawAPI.list_companies, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def get_company_inventory(session: aiohttp.ClientSession, user_id: int) -> CompanyIdInventoryGetOutput:
        """Get the company inventory."""

        async def caller(session: aiohttp.ClientSession) -> CompanyIdInventoryGetOutput:
            async with (
                session.get(f"/company/{user_id}/inventory") as resp,
            ):
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = "Company not found"
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.CompanyRawAPI.get_company_inventory,"
                    f" Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def get_company_achievement(session: aiohttp.ClientSession, user_id: int) -> CompanyIdAchievementGetOutput:
        """Get a list of company achievement."""

        async def caller(session: aiohttp.ClientSession) -> CompanyIdAchievementGetOutput:
            async with (
                session.get(f"/company/{user_id}/achievements") as resp,
            ):
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = "Company not found"
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.CompanyRawAPI.get_company_achievement,"
                    f" Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)


class ShopRawAPI:
    """A bundle of API available to use for company endpoint."""

    @staticmethod
    async def list_shop_items(  # noqa: PLR0913
        session: aiohttp.ClientSession,
        *,
        page: int = 1,
        limit: int = 10,
        sort: Literal["price", "quantity"] = "price",
        ascending: bool = True,
        is_disabled: bool | None = None,
    ) -> ShopGetOutput:
        """Get a list of item in the page in the shop through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> ShopGetOutput:
            params = {
                "page": page,
                "limit": limit,
                "sort": sort,
                "ascending": str(ascending),
            }
            if isinstance(is_disabled, bool):
                params["is_disabled"] = str(is_disabled)
            async with (
                session.get(
                    "/shop",
                    params=params,
                ) as resp,
            ):
                if resp.ok:
                    return (await resp.json())["shop_items"]
                if resp.status == Status.NOT_FOUND:
                    message = "No item found"
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.ShopRawAPI.list_shop_items," f" Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def patch_shop_item(session: aiohttp.ClientSession, item: ShopIdPatchInput) -> None:
        """Edit a item by its id in the shop through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> None:
            async with (
                session.patch(f"/shop/{item['item_id']}", json=item) as resp,
            ):
                if resp.ok:
                    return
                if resp.status == Status.NOT_FOUND:
                    message = f"Item with item id: {item['item_id']} not found"
                    raise DoesNotExistError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.ShopRawAPI.patch_shop_item, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def add_shop_item(session: aiohttp.ClientSession, item: ShopPostInput) -> None:
        """Create a item in the shop through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> None:
            async with (
                session.post("/shop", json=item) as resp,
            ):
                if resp.ok:
                    return
                if resp.status == Status.NOT_FOUND:
                    message = "Item have already existed"
                    raise AlreadyExistError(message)
                if resp.status == Status.BAD_REQUEST:
                    message = "Unable to create item"
                    raise UnknownNetworkError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.ShopRawAPI.add_shop_item, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def get_shop_item(session: aiohttp.ClientSession, item_id: int) -> RawShopItem:
        """Get a item by its id in the shop through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> RawShopItem:
            async with (
                session.get(f"/shop/{item_id}") as resp,
            ):
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = f"Item with item id: {item_id} not found"
                    raise DoesNotExistError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.ShopRawAPI.get_shop_item, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def purchase_shop_item(session: aiohttp.ClientSession, item_id: int, src: ShopBuyInput) -> ShopBuyOutput:
        """Get a item by its id and quantity in the shop through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> ShopBuyOutput:
            async with (
                session.put(f"/shop/{item_id}/buy", json=src) as resp,
            ):
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.UNAUTHORIZED:
                    await CompanyRawAPI.get_company(session, int(src["company_id"]))
                    message = "Not enough balance"
                    raise UserError(message)  # Should probably do further check on this
                if resp.status == Status.NOT_FOUND:
                    message = f"Item with item id: {item_id} not found"
                    raise DoesNotExistError(message)
                message = (
                    f"Undefined behaviour bot.src.wrapper.ShopRawAPI.purchase_shop_item, Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)


class UserRawAPI:
    """A bundle of API available to use for user endpoint."""

    @staticmethod
    async def get_user(session: aiohttp.ClientSession, user_id: int) -> UserIdGetOutput:
        """Get the User information by user id through direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> UserIdGetOutput:
            async with session.get(f"/user/{user_id}") as resp:
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = f"User with user id {user_id} cannot be found"
                    raise DoesNotExistError(message)
                message = f"Undefined behaviour bot.src.wrapper.UserRawAPI.get_user, Status received {resp.status}"
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def create_user(session: aiohttp.ClientSession, user_id: int) -> None:
        """Create the user by user id through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> None:
            async with session.post(f"/user/{user_id}") as resp:
                if resp.ok:
                    return
                if resp.status == Status.CONFLICT:
                    message = f"User with user id {user_id} have been register already"
                    raise AlreadyExistError(message)
                message = f"Undefined behaviour bot.src.wrapper.UserRawAPI.create_user, Status received {resp.status}"
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def update_user_experience(
        session: aiohttp.ClientSession, user_id: int, src: UserIdExperiencePatchInput
    ) -> UserIdExperiencePatchOutput:
        """Update the user experience by user id through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> UserIdExperiencePatchOutput:
            async with session.patch(f"/user/{user_id}/experience/add", json=src) as resp:
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = f"User with user id {user_id} cannot be found"
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.UserRawAPI.update_user_experience,"
                    f" Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def set_user_experience(
        session: aiohttp.ClientSession, user_id: int, src: UserIdExperiencePostInput
    ) -> UserIdExperiencePostOutput:
        """Set the user experience by user id through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> UserIdExperiencePatchOutput:
            async with session.post(f"user/{user_id}/experience/set", json=src) as resp:
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = f"User with user id {user_id} cannot be found"
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.UserRawAPI.set_user_experience,"
                    f" Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)


class AchievementRawAPI:
    @staticmethod
    async def get_achievements(session: aiohttp.ClientSession) -> AchievementGetOutput:
        """Get all achievements through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> AchievementGetOutput:
            async with session.get("/achievements") as resp:
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = "No achievements found."
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.AchievementRawAPI.get_achievements,"
                    f" Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)

    @staticmethod
    async def get_achievement(session: aiohttp.ClientSession, achievement_id: int) -> AchievementIdGetOutput:
        """Get the specific achievement through a direct HTTP request."""

        async def caller(session: aiohttp.ClientSession) -> AchievementIdGetOutput:
            async with session.get(f"/achievement/{achievement_id}") as resp:
                if resp.ok:
                    return await resp.json()
                if resp.status == Status.NOT_FOUND:
                    message = "Achievements not found."
                    raise DoesNotExistError(message)
                message = (
                    "Undefined behaviour bot.src.wrapper.AchievementRawAPI.get_achievement,"
                    f" Status received {resp.status}"
                )
                raise UnknownNetworkError(message)

        return await make_request(session, caller)
