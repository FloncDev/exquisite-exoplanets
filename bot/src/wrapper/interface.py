from typing import TYPE_CHECKING

from ._communication import CompanyRawAPI
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
