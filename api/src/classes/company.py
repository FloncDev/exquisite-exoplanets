# pyright: reportOptionalMemberAccess=false

from typing import TYPE_CHECKING, Any

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, desc, or_, select
from src.classes.pagination import CompanyPagination, Paginate
from src.models import Company, CompanyCreate, CompanyPublic, CompanyUpdate

if TYPE_CHECKING:
    from collections.abc import Sequence


class CompanyRepresentation:
    """Class that represents a `company` that is stored in the database."""

    def __init__(self, session: Session, *, company: Company | None = None) -> None:
        self.session: Session = session
        self.company: Company | None = company

    @classmethod
    def fetch_company(
        cls, session: Session, *, name: str | None = None, owner_id: str | None = None, company_id: int | None = None
    ) -> "CompanyRepresentation":
        """Return instance with target Company, if it exists.

        :param company_id: ID of the Company to search for.
        :param session: Database session.
        :param name: Name of the company.
        :param owner_id: ID of the Owner.
        :return: Instance with the fetched company.
        """
        fetched_company: Company | None = session.exec(
            select(Company).where(
                or_(Company.id.__eq__(company_id), Company.name.__eq__(name), Company.owner_id.__eq__(owner_id))
            )
        ).first()

        if not fetched_company:
            raise HTTPException(status_code=404, detail="Company cannot be found.")

        return cls(session=session, company=fetched_company)

    @classmethod
    def fetch_companies(cls, session: Session, params: CompanyPagination) -> dict[str, Any]:
        """Return Companies from the database and return them, with pagination.

        :param session: Database session.
        :param params: Pagination parameters.
        :return: Paginated response to return.
        """
        q: Any = select(Company)
        q = q.order_by(desc(Company.networth)) if not params.ascending else q.order_by(Company.networth)

        paginator: Paginate = Paginate(query=q, session=session, params=params)

        res: list[dict[str, Any]] = [{
            "name": company.name,
            "owner_id": company.owner_id,
            "networth": company.networth,
            "is_bankrupt": company.is_bankrupt,
        } for company in paginator.get_data()]

        # If nothing
        if not res:
            raise HTTPException(status_code=404, detail="Companies not found.")

        paginator.add_data({"companies": res})
        return paginator.get_page()

    @classmethod
    def create_company(cls, session: Session, data: CompanyCreate) -> "CompanyRepresentation":
        """Return instance with newly created Company.

        If the `owner` already has a company, they cannot create a new one.
        If the `name` has been taken, the company cannot be created.

        :param session: Database session.
        :param data: Company create data.
        :return: Instance with the created company.
        """
        # Query the database
        target: Sequence[Company] = session.exec(
            select(Company).where(or_(Company.name.__eq__(data.name), Company.owner_id.__eq__(data.owner_id)))
        ).all()

        if target and not any(x.is_bankrupt for x in target):
            raise HTTPException(status_code=409, detail="Such company already exists.")

        try:
            new_company: Company = Company(name=data.name, owner_id=data.owner_id)
            session.add(new_company)
            session.flush()
            session.commit()
            session.refresh(new_company)

        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(status_code=500, detail="Unable to create a new Company") from None

        return cls(session=session, company=new_company)

    def get_company(self) -> Company | None:
        """Get the Company model bound to the instance.

        :return: Bound Company model.
        """
        return self.company

    def get_details(self) -> CompanyPublic | None:
        """Get the details of the Company.

        :return: Company details.
        """
        if self.company is not None:
            return CompanyPublic.model_validate(self.company)
        return None

    def update(self, data: CompanyUpdate) -> None:
        """Update the Company's details.

        :param data: Data of Company to update.
        :return: None
        """
        try:
            has_changed: bool = False

            if data.name is not None:
                self.company.name = data.name
                has_changed = True

            if has_changed:
                self.session.add(self.company)
                self.session.flush()
                self.session.commit()

        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Unable to update Company.") from None

    def delete(self) -> None:
        """Mark the Company as `bankrupt`.

        :return: None
        """
        try:
            self.company.is_bankrupt = True
            self.session.add(self.company)
            self.session.flush()
            self.session.commit()

        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Unable to delete Company.") from None
