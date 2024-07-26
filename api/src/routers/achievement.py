from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.classes.achievements import AchievementRepresentation
from src.db import get_session
from src.models import AchievementPublic

router = APIRouter()


@router.get("/achievements")
async def get_achievements(session: Session = Depends(get_session)) -> dict[str, list[AchievementPublic]]:
    """Get all the Achievements available to collect.

    :param session: Database session.
    :return: All Achievements
    """
    achievements: list[AchievementPublic] = [
        x.get_details() for x in AchievementRepresentation.fetch_achievements(session=session)
    ]
    return {"achievements": achievements}


@router.get("/achievement/{achievement_id}")
async def get_achievement(achievement_id: int, session: Session = Depends(get_session)) -> AchievementPublic:
    """Get the details of the given Achievement.

    :param achievement_id: ID of the Achievement to get.
    :param session: Database session.
    :return: Achievement details.
    """
    return AchievementRepresentation.fetch_achievement(session=session, achievement_id=achievement_id).get_details()
