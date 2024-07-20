from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from ._communication import CompanyRawAPI
from .error import DoNotExistError
from .schema import Company

if TYPE_CHECKING:
    from ._api_schema import CompanyGetIdOutput, CompanyPatchIdInput, CompanyPostInput


class BaseAPI:
    """A BaseAPI with the required argument."""

    def __init__(self, address: str, token: str) -> None:
        self.address = address
        self.token = token


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


class Interface:
    """An API wrapper interface for the bot."""

    def __init__(self, address: str, token: str) -> None:
        """Initialize the interface with the address and API token."""
        self.address = address
        self.token = token

    @property
    def company(self) -> CompanyAPI:
        """Retrieve the Company API with the address and Token."""
        return CompanyAPI(self.address, self.token)
