from fastapi import FastAPI, Depends
from fastapi import HTTPException
from sqlmodel import Session, SQLModel
from uvicorn import run

from .classes.company import CompanyRepresentation
from .classes.pagination import CompanyPagination
from .db import engine, get_session
from .models import CompanyCreate, CompanyUpdate

SQLModel.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/company")
async def create_company(data: CompanyCreate, session: Session = Depends(get_session)):
    """
    Endpoint to create a new Company.

    :param data: Company data.
    :param session: Database session.
    :return: Success or not.
    """
    # Creating the company
    try:
        _ = CompanyRepresentation.create_company(session=session, data=data)

    except HTTPException as ex:
        raise ex

    raise HTTPException(status_code=201, detail="Company created successfully.")


@app.get("/company/{company_id}")
async def get_company(company_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to get the target Company.

    :param company_id: ID of Company to get.
    :param session: Database session.
    :return: Fetched Company.
    """
    try:
        fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(
            session=session, company_id=company_id
        )
        return fetched_company.get_details()

    except HTTPException as ex:
        raise ex


@app.get("/companies")
async def get_companies(params: CompanyPagination = Depends(), session: Session = Depends(get_session)):
    """
    Endpoint to get all Companies, with pagination.

    :param params: Endpoint parameters.
    :param session: Database session.
    :return: Fetched, paginated Companies
    """
    try:
        return CompanyRepresentation.fetch_companies(session=session, params=params)

    except HTTPException as ex:
        raise ex


@app.patch("/company/{company_id}")
async def update_company(company_id: int, data: CompanyUpdate, session: Session = Depends(get_session)):
    """
    Endpoint to update the given Company's details.

    :param data: Data to update.
    :param session: Database session.
    :return: None
    """
    try:
        fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(
            session=session, company_id=company_id
        )
        fetched_company.update(data=data)

    except HTTPException as ex:
        raise ex

    return HTTPException(status_code=200, detail="Company successfully updated.")


@app.delete("/company/{company_id}")
async def delete_company(company_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to delete the given Company. Marks them as `bankrupt`.

    :param session: Database session.
    :return: None
    """
    try:
        fetched_company: CompanyRepresentation = CompanyRepresentation.fetch_company(
            session=session, company_id=company_id
        )
        fetched_company.delete()

    except HTTPException as ex:
        raise ex

    return HTTPException(status_code=200, detail="Company successfully deleted.")


def main() -> None:
    """Create the database tables"""
    run("src.main:app", reload=False)
