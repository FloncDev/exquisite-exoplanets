from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.classes.company import CompanyRepresentation
from src.classes.pagination import CompanyPagination
from src.db import get_session
from src.models import CompanyCreate, CompanyPublic, CompanyUpdate

router = APIRouter()


@router.post("/company")
async def create_company(data: CompanyCreate, session: Session = Depends(get_session)) -> None:
    """Endpoint to create a new Company.

    :param data: Company data.
    :param session: Database session.
    :return: Success or not.
    """
    # Creating the company
    CompanyRepresentation.create_company(session=session, data=data)
    raise HTTPException(status_code=201, detail="Company created successfully.")


@router.get("/company/{company_id}")
async def get_company(company_id: int, session: Session = Depends(get_session)) -> CompanyPublic | None:
    """Endpoint to get the target Company.

    :param company_id: ID of Company to get.
    :param session: Database session.
    :return: Fetched Company.
    """
    fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(session=session, company_id=company_id)
    return fetched_company.get_details()


@router.get("/companies")
async def get_companies(
    params: CompanyPagination = Depends(),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Endpoint to get all Companies, with pagination.

    :param params: Endpoint parameters.
    :param session: Database session.
    :return: Fetched, paginated Companies
    """
    return CompanyRepresentation.fetch_companies(session=session, params=params)


@router.patch("/company/{company_id}")
async def update_company(company_id: int, data: CompanyUpdate, session: Session = Depends(get_session)) -> None:
    """Endpoint to update the given Company's details.

    :param company_id: ID of the Company to update.
    :param data: Data to update.
    :param session: Database session.
    :return: None
    """
    fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(session=session, company_id=company_id)
    fetched_company.update(data=data)
    raise HTTPException(status_code=200, detail="Company successfully updated.")


@router.delete("/company/{company_id}")
async def delete_company(company_id: int, session: Session = Depends(get_session)) -> None:
    """Endpoint to delete the given Company. Marks them as `bankrupt`.

    :param company_id: ID of the Company to delete.
    :param session: Database session.
    :return: None
    """
    fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(session=session, company_id=company_id)
    fetched_company.delete()

    raise HTTPException(status_code=200, detail="Company successfully deleted.")


@router.get("/company/{company_id}/inventory")
async def get_inventory(company_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    return CompanyRepresentation.fetch_company(session=session, company_id=company_id).get_inventory()
