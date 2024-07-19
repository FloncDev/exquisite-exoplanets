from enum import IntEnum

import aiohttp

from ._api_schema import CompanyPostInput
from .error import AlreadyExistError, UnknownNetworkError


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
