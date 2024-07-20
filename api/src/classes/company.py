from typing import Dict, Any, List

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, or_, select, desc

from src.classes.pagination import CompanyPagination, Paginate
from src.models import Company, CompanyCreate, CompanyPublic


class CompanyRepresentation:
    """Class that represents a `company` that is stored in the database"""

    def __init__(self, session: Session, *, company: Company | None = None):
        self.session: Session = session
        self.company: Company | None = company

    @classmethod
    def fetch_company(
        cls, session: Session, *, name: str | None = None, owner_id: str | None = None, company_id: int | None = None
    ) -> "CompanyRepresentation":
        """
        Method to fetch a company from the database, if it exists.

        :param company_id: ID of the Company to search for.
        :param session: Database session.
        :param name: Name of the company.
        :param owner_id: ID of the Owner.
        :return: Instance with the fetched company.
        """
        fetched_company: Company | None = session.exec(
            select(Company).where(
                or_(Company.id.__eq__(company_id), Company.name.__eq__(name), Company.owner.__eq__(owner_id))
            )
        ).first()

        if not fetched_company:
            raise HTTPException(status_code=404, detail="Company cannot be found.")

        return cls(session=session, company=fetched_company)

    @classmethod
    def fetch_companies(cls, session: Session, params: CompanyPagination) -> Dict[str, Any]:
        """
        Method to get Companies from the database and return them, with pagination.

        :param session: Database session.
        :param params: Pagination parameters.
        :return: Paginated response to return.
        """
        q: Any = select(Company)
        q = q.order_by(desc(Company.networth)) if not params.ascending else q.order_by(Company.networth)

        paginator: Paginate = Paginate(query=q, session=session, params=params)

        res: List[Dict[str, Any]] = []
        for company in paginator.get_data():
            company = company[0]  # type: ignore
            res.append({"name": company.name, "owner": company.owner, "networth": company.networth})

        # If nothing
        if not res:
            raise HTTPException(status_code=404, detail="Companies not found.")

        paginator.add_data({"companies": res})
        return paginator.get_page()

    @classmethod
    def create_company(cls, session: Session, data: CompanyCreate) -> "CompanyRepresentation":
        """
        Method to create a new Company and store in the database.

        If the `owner` already has a company, they cannot create a new one.
        If the `name` has been taken, the company cannot be created.

        :param session: Database session.
        :param data: Company create data.
        :return: Instance with the created company.
        """
        # Query the database
        target: Company | None = session.exec(
            select(Company).where(or_(Company.name.__eq__(data.name), Company.owner.__eq__(data.owner)))
        ).first()

        if target:
            raise HTTPException(status_code=409, detail="Such company already exists.")

        try:
            new_company: Company = Company(name=data.name, owner=data.owner)
            session.add(new_company)
            session.flush()
            session.commit()
            session.refresh(new_company)

        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(status_code=500, detail="Unable to create a new Company")

        return cls(session=session, company=new_company)

    def get_company(self) -> Company | None:
        """
        Get the Company model bound to the instance.

        :return: Bound Company model.
        """
        return self.company

    def get_details(self) -> CompanyPublic | None:
        """
        Get the details of the Company.

        :return: Company details.
        """
        if self.company is not None:
            return CompanyPublic.model_validate(self.company[0])  # type: ignore
        return None
