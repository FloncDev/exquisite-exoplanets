from typing import TYPE_CHECKING, Any, Self

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, desc, not_, or_, select
from src.classes.pagination import CompanyPagination, Paginate
from src.classes.user import UserRepresentation
from src.models import (
    Achievement,
    AchievementsCompanyPublic,
    Company,
    CompanyCreate,
    CompanyPublic,
    CompanyUpdate,
    EarnedAchievements,
    Inventory,
    InventoryPublic,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class CompanyRepresentation:
    """Class that represents a `company` that is stored in the database."""

    def __init__(self, session: Session, company: Company) -> None:
        self.session: Session = session
        self.company: Company = company

    @classmethod
    def fetch_company(cls, session: Session, company_id: str) -> Self:
        """Return instance with target Company, if it exists.

        :param company_id: ID of the Company to search for.
        :param session: Database session.
        :return: Instance with the fetched company.
        """
        fetched_company: Company | None = session.exec(
            select(Company).where(Company.owner_id == company_id, not_(Company.is_bankrupt))
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

        res: list[dict[str, Any]] = [
            {
                "name": company.name,
                "owner_id": company.owner_id,
                "networth": company.networth,
                "is_bankrupt": company.is_bankrupt,
            }
            for company in paginator.get_data()
        ]

        # If nothing
        if not res:
            raise HTTPException(status_code=404, detail="Companies not found.")

        paginator.add_data({"companies": res})
        return paginator.get_page()

    @classmethod
    def create_company(cls, session: Session, data: CompanyCreate) -> Self:
        """Return instance with newly created Company.

        If the `owner` already has a company, they cannot create a new one.
        If the `name` has been taken, the company cannot be created.

        :param session: Database session.
        :param data: Company create data.
        :return: Instance with the created company.
        """
        # Getting the User
        fetched_user: UserRepresentation = UserRepresentation.fetch_user(session=session, user_id=data.owner_id)

        # Query the database
        target: Sequence[Company] = session.exec(
            select(Company).where(or_(Company.name == data.name, Company.owner_id == data.owner_id))
        ).all()

        if target and not any(x.is_bankrupt for x in target):
            raise HTTPException(status_code=409, detail="Such company already exists.")

        try:
            new_company: Company = Company(name=data.name, owner_id=fetched_user.get_user().user_id)
            session.add(new_company)
            session.commit()
            session.refresh(new_company)

        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(status_code=500, detail="Unable to create a new Company") from None

        return cls(session=session, company=new_company)

    def get_company(self) -> Company:
        """Get the Company model bound to the instance.

        :return: Bound Company model.
        """
        return self.company

    def get_details(self) -> CompanyPublic:
        """Get the details of the Company.

        :return: Company details.
        """
        return CompanyPublic.model_validate(self.company)

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
            self.session.commit()

        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Unable to delete Company.") from None

    def get_inventory(self) -> dict[str, Any]:
        """Get the Company's Inventory.

        :return: Company's inventory.
        """
        inventory: list[Inventory] | None = self.company.inventory

        res: list[InventoryPublic] = []

        for item in inventory:
            data: dict[str, Any] = {
                "company_id": item.company_id,
                "stock": item.stock,
                "total_amount_spent": item.total_amount_spent,
                "item": {"item_id": item.item.id, "name": item.item.name},
            }
            res.append(InventoryPublic.model_validate(data))

        return {"company_id": self.company.id, "inventory": res}

    def get_achievements(self) -> AchievementsCompanyPublic:
        """Get the Achievements the Company has achieved.

        :return: Company's Achievements.
        """
        company_achievements: list[EarnedAchievements] = self.company.achievements

        if not company_achievements:
            raise HTTPException(status_code=404, detail="Company has no Achievements.")

        achievements_details: list[AchievementsCompanyPublic.AchievementSingle] = []
        for achievement in company_achievements:
            ach: Achievement = achievement.achievement
            details: dict[str, Any] = {"id": ach.id, "name": ach.name, "description": ach.description}
            achievements_details.append(AchievementsCompanyPublic.AchievementSingle.model_validate(details))

        # Getting the Company's first and latest Achievement
        company_achievements = sorted(company_achievements, key=lambda x: x.achieved, reverse=False)
        first_achievement, latest_achievement = company_achievements[0], company_achievements[-1]

        res: dict[str, Any] = {
            "achievements": achievements_details,
            "first_achievement": first_achievement.achievement.name,
            "latest_achievement": latest_achievement.achievement.name,
        }

        return AchievementsCompanyPublic.model_validate(res)
