from typing import TypedDict


class CompanyPostInput(TypedDict):
    company_name: str
    owner_id: int


class CompanyPostOutput(TypedDict):
    company_name: str
    owner_id: int
    created_date: str


class CompanyPostIdOutput(CompanyPostOutput):
    is_bankrypt: bool
    current_networth: float


class CompanyPatchIdInput(TypedDict):
    company_name: str
