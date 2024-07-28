from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.classes.company import CompanyRepresentation
from src.classes.pagination import CompanyPagination
from src.db import get_session
from src.models import AchievementsCompanyPublic, CompanyCreate, CompanyPublic, CompanyUpdate, ResourceCollectionPublic

router = APIRouter()


@router.post("/company", status_code=201)
async def create_company(data: CompanyCreate, session: Session = Depends(get_session)) -> CompanyPublic:
    """Endpoint to create a new Company.

    :param data: Company data.
    :param session: Database session.
    :return: Success or not.
    """
    # Creating the company
    return CompanyRepresentation.create_company(session=session, data=data).get_details()


@router.get("/company/{company_id}")
async def get_company(company_id: str, session: Session = Depends(get_session)) -> CompanyPublic | None:
    """Endpoint to get the target Company.

    :param company_id: ID of Company to get.
    :param session: Database session.
    :return: Fetched Company.
    """
    fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(
        session=session, company_id=company_id
    )
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


@router.patch("/company/{company_id}", status_code=200)
async def update_company(
        company_id: str, data: CompanyUpdate, session: Session = Depends(get_session)
) -> dict[str, str]:
    """Endpoint to update the given Company's details.

    :param company_id: ID of the Company to update.
    :param data: Data to update.
    :param session: Database session.
    :return: None
    """
    fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(
        session=session, company_id=company_id
    )
    fetched_company.update(data=data)
    return {"message": "Company successfully updated."}


@router.delete("/company/{company_id}")
async def delete_company(company_id: str, session: Session = Depends(get_session)) -> dict[str, str]:
    """Endpoint to delete the given Company. Marks them as `bankrupt`.

    :param company_id: ID of the Company to delete.
    :param session: Database session.
    :return: None
    """
    fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(
        session=session, company_id=company_id
    )
    fetched_company.delete()
    return {"message": "Company successfully deleted."}


@router.get("/company/{company_id}/inventory")
async def get_inventory(company_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    return CompanyRepresentation.fetch_company(session=session, company_id=company_id).get_inventory()


@router.get("/company/{company_id}/achievements")
async def get_company_achievements(
        company_id: str, session: Session = Depends(get_session)
) -> AchievementsCompanyPublic:
    """Get the Achievements for the given Company.

    :param company_id: ID of Company.
    :param session: Database session.
    :return: Company's achievements.
    """
    return CompanyRepresentation.fetch_company(session=session, company_id=company_id).get_achievements()


@router.get("/company/{company_id}/collect")
def collect_resources(company_id: str, session: Session = Depends(get_session)) -> ResourceCollectionPublic:
    """Collect the resources on the Planet."""
    return CompanyRepresentation.fetch_company(session=session, company_id=company_id).collect_resources()
