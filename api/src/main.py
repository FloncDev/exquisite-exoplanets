import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, select
from src.db import engine
from uvicorn import run

from .routers import achievement, company, shop, user

SQLModel.metadata.create_all(bind=engine)


def _populate_achievements() -> None:
    """Populate the Achievements table."""
    from src.models import Achievement as AchievementModel

    reach_level_5: AchievementModel = AchievementModel(
        name="Reach level 5.", description="Achievement earned when reaching Level 5."
    )
    reach_level_10: AchievementModel = AchievementModel(
        name="Reach level 10.", description="Achievement earned when reaching Level 10."
    )
    reach_level_20: AchievementModel = AchievementModel(
        name="Reach level 20.", description="Achievement earned when reaching Level 20."
    )
    reach_level_30: AchievementModel = AchievementModel(
        name="Reach level 30.", description="Achievement earned when reaching Level 30."
    )
    reach_leaderboard: AchievementModel = AchievementModel(
        name="Leaderboard Achieved!", description="Achievement earned after finding your way onto the Leaderboard!"
    )

    all_achievements: list[AchievementModel] = [
        reach_level_5,
        reach_level_10,
        reach_level_20,
        reach_level_30,
        reach_leaderboard,
    ]

    with Session(engine) as session:
        for ach in all_achievements:
            found: AchievementModel | None = session.exec(
                select(AchievementModel).where(AchievementModel.name == ach.name)
            ).first()

            if found is None:
                session.add(ach)

        try:
            session.commit()

        except SQLAlchemyError:
            session.rollback()
            print("Cannot load achievements.")
            sys.exit(0)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001, ANN201
    _populate_achievements()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(company.router)
app.include_router(user.router)
app.include_router(shop.router)
app.include_router(achievement.router)


def main() -> None:
    """Create the database tables."""
    run("src.main:app", reload=True)
