from typing import TYPE_CHECKING

from ._communication import CompanyRawAPI
from .schema import Company

if TYPE_CHECKING:
    from ._api_schema import CompanyGetIdOutput, CompanyPostInput


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
        out: CompanyGetIdOutput = await CompanyRawAPI.get_company(self.address, self.token, user_id)
        return Company.from_dict(out)


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
