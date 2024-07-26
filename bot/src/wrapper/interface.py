from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import aiohttp

from ._communication import CompanyRawAPI, ShopRawAPI, UserRawAPI
from .error import DoesNotExistError, UserError
from .schema import Company, ShopItem, User

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
        """Create a company for the user and return the Company.

        :raise AlreadyExistError: Raise when the company name is already being used by other user,
         or the user already own a company
        :raise DoesNotExistError: The company cannot be found after an attempt of creation
        """
        src: CompanyPostInput = {"name": company_name, "owner_id": user_id}
        await CompanyRawAPI.create_company(self.parent.session, src)
        return await self.get_company(user_id)

    async def get_company(self, user_id: int) -> Company:
        """Get the company from user id.

        :raise DoesNotExistError: The user cannot be found from the given user_id
        """
        out: CompanyGetIdOutput = await CompanyRawAPI.get_company(self.parent.session, user_id)
        return Company.from_dict(out)

    async def edit_company_name(self, company: Company | int, new_name: str) -> Company:
        """Edit the company name with the given user id.

        :raise DoesNotExistError: The company cannot be found
        """
        if isinstance(company, Company):
            user_id: int = company.owner_id
        else:
            user_id: int = company
        src: CompanyPatchIdInput = {"company_name": new_name}
        await CompanyRawAPI.edit_company_name(self.parent.session, user_id, src)
        return await self.get_company(user_id)

    async def delete_company(self, company: Company | int) -> None:
        """Delete the company with the given Company object or user ID.

        :raise DoesNotExistError: The company cannot be found
        """
        if isinstance(company, Company):
            user_id: int = company.owner_id
        else:
            user_id: int = company
        await CompanyRawAPI.delete_company(self.parent.session, user_id)

    async def list_companies(self, page: int = 1, limit: int = 10) -> list[Company]:
        """List companies from the database using paginator.

        :raise DoesNotExistError: Reach the end of the paginator where no more company could be displayed
        """
        return [
            Company.from_dict(out)
            for out in await CompanyRawAPI.list_companies(self.parent.session, page=page, limit=limit)
        ]

    async def iter_companies(self) -> AsyncGenerator[Company, None]:
        """Iterate through all company until there are no company left."""
        page = 1
        while True:
            try:
                for company in await self.list_companies(page=page):
                    yield company
                page += 1
            except DoesNotExistError:
                return

    async def get_inventory(self, company: Company | int) -> Company:
        """Get the inventory of the company.

        :param company: A company object or the company ID
        :return: A company object with current inventory
        :raise DoesNotExistError: The company referencing doesn't exist on the server
        """
        check_company: Company
        if isinstance(company, int):
            check_company = await self.get_company(company)
        else:
            check_company = company
        check_company.set_inventory(
            await CompanyRawAPI.get_company_inventory(self.parent.session, check_company.owner_id)
        )
        return check_company


class ShopAPI(BaseAPI):
    """Bundle of formatted API access to shop endpoint."""

    async def list_items(  # noqa: PLR0913
        self,
        *,
        page: int = 1,
        limit: int = 10,
        sort: Literal["price", "quantity"] = "price",
        ascending: bool = True,
        is_disabled: bool | None = None,
    ) -> list[ShopItem]:
        """Return a list of shop items.

        :raise DoesNotExistError: No item from the current page have been found
        """
        return [
            ShopItem.from_dict(out)
            for out in await ShopRawAPI.list_shop_items(
                self.parent.session, page=page, limit=limit, sort=sort, ascending=ascending, is_disabled=is_disabled
            )
        ]

    async def iter_items(
        self,
        *,
        sort: Literal["price", "quantity"] = "price",
        ascending: bool = True,
        is_disabled: bool | None = None,
    ) -> AsyncGenerator[ShopItem, None]:
        """Iterate through all item until there are no item left."""
        page = 1
        while True:
            try:
                for item in await self.list_items(page=page, sort=sort, ascending=ascending, is_disabled=is_disabled):
                    yield item
                page += 1
            except DoesNotExistError:
                return

    async def get_shop_item(self, item_id: int) -> ShopItem:
        """Get a specific shop item.

        :raise DoesNotExistError: The item cannot be found with the item_id
        """
        return ShopItem.from_dict(await ShopRawAPI.get_shop_item(self.parent.session, item_id))

    async def create_shop_item(
        self, item: ShopItem | None = None, /, *, name: str, price: float, quantity: int
    ) -> None:
        """Create an item with the ShopItem or(xor) the name, price and quantity of the item.

        :param item: An `ShopItem` created from `ShopItem.from_future_definition`
        :param name: The name of the item, Do not supply together with `item`
        :param price: The price of the item, Do not supply together with `item`
        :param quantity: The quantity of the item, Do not supply together with `item`
        :raise ValueError: The shop item and the creation parameter have been supply at the same time
        :raise UserError: The item is not created with `ShopItem.from_future_definition` and the `item_id` is not -1
        :raise AlreadyExistError: The item have already exist
        """
        if item and any((name, price, quantity)):
            msg = "A shop item and the creation parameter have been supply at the same time"
            raise ValueError(msg)
        if item:
            create_item: ShopItem = item
        else:
            create_item = ShopItem.from_future_definition(name=name, price=price, quantity=quantity)
        try:
            item_definition = create_item.to_creation()
        except ValueError as exc:
            msg = "The item is not created properly"
            raise UserError(msg) from exc
        await ShopRawAPI.add_shop_item(self.parent.session, item_definition)

    async def patch_item(self, item: ShopItem) -> None:
        """Edit the item with the ShopItem with edited attribute.

        :param item: A shop item with edited parameter
        :raise DoesNotExistError: The item doesn't exist
        """
        if item.item_id == -1:
            message = f"The item does not have a valid item ID: {item.item_id}"
            raise DoesNotExistError(message)

        await ShopRawAPI.patch_shop_item(self.parent.session, item.to_modify())

    async def purchase(self, item: ShopItem | int, company: Company | int, quantity: int) -> None:
        """Purchase item as the company.

        :raise DoesNotExistError: The company the user own cannot be found or the item cannot be found
        :raise UserError: The company doesn't have enough balance to purchase the item
        """
        if isinstance(item, ShopItem):
            item_id: int = item.item_id
        else:
            item_id: int = item
        if isinstance(company, Company):
            user_id: int = company.owner_id
        else:
            user_id: int = company
        await ShopRawAPI.purchase_shop_item(self.parent.session, item_id, {"user_id": user_id, "quantity": quantity})


class UserAPI(BaseAPI):
    """Bundle of formatted API access to api endpoint."""

    async def register_user(self, user_id: int) -> User:
        """Register the user by the user_id.

        :param user_id: A user id for the user to be registered
        :return: A `User` object
        :raise AlreadyExistError: Raise when the user already existed
        :raise DoesNotExistError: The user cannot be found after an attempt of registration
        """
        await UserRawAPI.create_user(self.parent.session, user_id)
        return await self.get_user(user_id)

    async def get_user(self, user: User | int) -> User:
        """Get the user by its user_id, or a updated User object from the User object.

        :param user: A `User` object or a user id
        :return: A `User` object
        :raise DoesNotExistError: The user cannot be found
        """
        if isinstance(user, User):
            user_id: int = user.user_id
        else:
            user_id: int = user

        return User.from_dict(await UserRawAPI.get_user(self.parent.session, user_id))

    async def add_experience(self, user: User | int, exp: int = 0) -> tuple[bool, User]:
        """Update the amount of experience the user have.

        :param user: A `User` object or a user id
        :param exp: the added experience to the user
        :return: A boolean value represent whether the user have upgraded, and
         User represent an updated user after adding experience
        :raise DoesNotExistError: The user cannot be found
        """
        if isinstance(user, User):
            user_id: int = user.user_id
        else:
            user_id: int = user

        result = await UserRawAPI.update_user_experience(self.parent.session, user_id, {"new_experience": exp})
        return result["level_up"], await self.get_user(user_id)

    async def set_experience(self, user: User | int, exp: int = 0) -> tuple[bool, User]:
        """Update the amount of experience the user have.

        :param user: A `User` object or a user id
        :param exp: the amount of experience set to the user
        :return: A boolean value represent whether the user have upgraded, and
         User represent an updated user after adding experience
        :raise DoesNotExistError: The user cannot be found
        """
        if isinstance(user, User):
            user_id: int = user.user_id
        else:
            user_id: int = user

        result = await UserRawAPI.set_user_experience(self.parent.session, user_id, {"experience": exp})
        return result["level_up"], await self.get_user(user_id)


class Interface:
    """An API wrapper interface for the bot."""

    def __init__(self, address: str, token: str) -> None:
        """Initialize the interface with the address and API token."""
        self.address = address
        self.token = token
        self._session: aiohttp.ClientSession = aiohttp.ClientSession(
            base_url=address, headers={"Authorization": token}
        )

    @property
    def company(self) -> CompanyAPI:
        """Retrieve the Company API with the address and Token."""
        return CompanyAPI(self.address, self.token, parent=self)

    @property
    def shop(self) -> ShopAPI:
        """Retrieve the Shop API with the address and Token."""
        return ShopAPI(self.address, self.token, parent=self)

    @property
    def user(self) -> UserAPI:
        """Retrieve the User API with the address and Token."""
        return UserAPI(self.address, self.token, parent=self)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Return the state of the session and the session."""
        return self._session
