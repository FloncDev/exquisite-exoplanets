from typing import TYPE_CHECKING, Any, Self

from fastapi import HTTPException
from sqlmodel import Session, select
from src.models import Achievement, AchievementPublic, CompanyAchievementPublic, EarnedAchievements

if TYPE_CHECKING:
    from collections.abc import Sequence


class AchievementRepresentation:
    """Class representing an `achievement` in the database."""

    def __init__(self, session: Session, achievement: Achievement) -> None:
        self.session: Session = session
        self.achievement: Achievement = achievement

    @classmethod
    def fetch_achievement(cls, session: Session, achievement_id: int) -> Self:
        """Fetch the target Achievement.

        :param session: Database session.
        :param achievement_id: ID of achievement to fetch.
        :return: Details of the achievement.
        """
        fetched_achievement: Achievement | None = session.exec(
            select(Achievement).where(Achievement.id == achievement_id)
        ).first()

        if fetched_achievement is None:
            raise HTTPException(status_code=404, detail="Achievement not found.")

        return cls(session=session, achievement=fetched_achievement)

    @classmethod
    def fetch_achievements(cls, session: Session) -> list[Self]:
        """Get all the Achievements from the database.

        :param session: Database session.
        :return: List of all Achievements.
        """
        fetched_achievements: Sequence[Achievement] = session.exec(select(Achievement)).all()

        if len(fetched_achievements) == 0:
            raise HTTPException(status_code=404, detail="Achievements not found.")

        return [cls(session=session, achievement=fetched_achievement) for fetched_achievement in fetched_achievements]

    def get_achievement(self) -> Achievement:
        """Get the Achievement bound to the object instance.

        :return: Bound Achievement.
        """
        return self.achievement

    def get_details(self) -> AchievementPublic:
        """Get the details of the Achievement.

        :return: Achievement details.
        """
        details: dict[str, Any] = {
            "id": self.achievement.id,
            "name": self.achievement.name,
            "description": self.achievement.description,
        }

        # Getting the Companies that have earned the given achievement.
        companies_earned: list[EarnedAchievements] = self.achievement.companies_earned

        if not companies_earned:
            details["companies_earned"] = 0
            details["first_achieved"] = None
            details["latest_achieved"] = None

        else:
            # Get the company that 1) earned it first, 2) earned it the latest
            companies_earned = sorted(companies_earned, key=lambda x: x.achieved, reverse=False)
            first_company: EarnedAchievements = companies_earned[0]
            latest_company: EarnedAchievements = companies_earned[-1]

            details["companies_earned"] = len(companies_earned)
            details["first_achieved"] = CompanyAchievementPublic.model_validate(
                {
                    "name": first_company.achievement.name,
                    "owner_id": first_company.company.owner_id,
                    "date": first_company.achieved,
                }
            )
            details["latest_achieved"] = CompanyAchievementPublic.model_validate(
                {
                    "name": latest_company.achievement.name,
                    "owner_id": latest_company.company.owner_id,
                    "date": latest_company.achieved,
                }
            )

        return AchievementPublic.model_validate(details)
