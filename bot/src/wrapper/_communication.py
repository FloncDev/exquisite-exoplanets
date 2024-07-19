from enum import IntEnum

import aiohttp

from ._api_schema import BatchCompaniesOutput, CompanyPatchIdInput, CompanyPostIdOutput, CompanyPostInput
from .error import AlreadyExistError, DoNotExistError, UnknownNetworkError


class Status(IntEnum):
    """Store the used http status code from the api."""

    OK = 200
    OK_CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409


async def create_company(address: str, token: str, src: CompanyPostInput) -> None:
    """Send an api request to create a company."""
    async with (
        aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
        session.post("/company", json=src) as resp,
    ):
        if resp.ok:
            return
        if resp.status == Status.CONFLICT:
            message = "This company name is already being used or The user already own a company"
            raise AlreadyExistError(message)
        message = f"Undefined behaviour bot.src.wrapper.create_company, Status received {resp.status}"
        raise UnknownNetworkError(message)


async def get_company(address: str, token: str, user_id: int) -> CompanyPostIdOutput:
    """Send an api request to get info of the company."""
    async with (
        aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
        session.get(f"/company/{user_id}") as resp,
    ):
        if resp.ok:
            return await resp.json()
        if resp.status == Status.NOT_FOUND:
            message = "This user doesn't own a company"
            raise DoNotExistError(message)
        message = f"Undefined behaviour bot.src.wrapper.get_company, Status received {resp.status}"
        raise UnknownNetworkError(message)


async def edit_company_name(address: str, token: str, user_id: int, src: CompanyPatchIdInput) -> None:
    """Send an api request to edit the company name."""
    async with (
        aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
        session.patch(f"/company/{user_id}", json=src) as resp,
    ):
        if resp.ok:
            return
        if resp.status == Status.NOT_FOUND:
            message = "This user doesn't own a company"
            raise DoNotExistError(message)
        message = f"Undefined behaviour bot.src.wrapper.edit_company_name, Status received {resp.status}"
        raise UnknownNetworkError(message)


async def delete_company(address: str, token: str, user_id: int) -> None:
    """Send an api request to delete the company."""
    async with (
        aiohttp.ClientSession(base_url=address, headers={"Authorization": token}) as session,
        session.delete(f"/company/{user_id}") as resp,
    ):
        if resp.ok:
            return
        if resp.status == Status.NOT_FOUND:
            message = "This user doesn't own a company"
            raise DoNotExistError(message)
        message = f"Undefined behaviour bot.src.wrapper.delete_company, Status received {resp.status}"
        raise UnknownNetworkError(message)


async def list_companies(address: str, token: str, page: int = 1, limit: int = 10) -> BatchCompaniesOutput:
    """Send an api request to return a list of companies."""
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
        message = f"Undefined behaviour bot.src.wrapper.list_companies, Status received {resp.status}"
        raise UnknownNetworkError(message)
