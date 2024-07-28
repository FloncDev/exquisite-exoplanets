import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, select
from src.db import engine
from src.yaml_reader import YamlReader
from uvicorn import run

from .models import (
    PlanetModel,
    PlanetResourcesModel,
    ResourceCollectorMineableResourcesModel,
    ResourceCollectorModel,
    ResourceModel,
)
from .planet import Planet
from .routers import achievement, collector, company, planet, resource, shop, user

if TYPE_CHECKING:
    from collections.abc import Sequence

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


def _populate_planets() -> None:
    """Populate the Planets table with what is in the config."""
    # Default starting planet
    starting_planet: dict[str, Any] = {
        "planet_id": "EA0000",
        "name": "Earth",
        "tier": 0,
        "description": "This empty husk used to be the most magnificent green world, believe it or not",
    }

    planets: dict[str, Any] = YamlReader("Planet.yaml").contents

    with Session(engine) as session:
        # insert default starting planet
        fetched_starting_planet: PlanetModel | None = session.exec(
            select(PlanetModel).where(PlanetModel.planet_id == starting_planet["planet_id"])
        ).first()

        if not fetched_starting_planet:
            session.add(PlanetModel.model_validate(starting_planet))

        for planet_id, data in planets.items():
            # Check if the Planet exists.
            # Only store if it does not exists
            fetched_planet: PlanetModel | None = session.exec(
                select(PlanetModel).where(PlanetModel.planet_id == planet_id)
            ).first()

            if fetched_planet is None:
                # Add new planet to the
                data["planet_id"] = planet_id
                new_planet: PlanetModel = PlanetModel.model_validate(data)
                session.add(new_planet)

        try:
            session.commit()

        except SQLAlchemyError:
            session.rollback()
            print("Cannot load Planets.")
            sys.exit(0)


def _populate_resources() -> None:
    """Populate the Resources table with what is in the config."""
    resource_contents: dict[str, Any] = YamlReader("Resource.yaml").contents

    with Session(engine) as session:
        for resource_id, data in resource_contents.items():
            # Check if the resource exists.
            # Only store if it does not exists
            fetched_resource: ResourceModel | None = session.exec(
                select(ResourceModel).where(ResourceModel.resource_id == resource_id)
            ).first()

            if fetched_resource is None:
                # Add new resource to the
                data["resource_id"] = resource_id
                new_resource: ResourceModel = ResourceModel.model_validate(data)
                session.add(new_resource)

        try:
            session.commit()

        except SQLAlchemyError:
            session.rollback()
            print("Cannot load Resources.")
            sys.exit(0)


def _populate_resource_collectors() -> None:
    """Populate the Resource Collectors table with what is in the config."""
    resource_collectors: dict[str, Any] = YamlReader("ResourceCollector.yaml").contents

    with Session(engine) as session:
        for collector_id, data in resource_collectors.items():
            # Check if the resource exists.
            # Only store if it exists
            fetched_collector: ResourceCollectorModel | None = session.exec(
                select(ResourceCollectorModel).where(ResourceCollectorModel.collector_id == collector_id)
            ).first()

            if fetched_collector is None:
                # Add new collector to the
                data["collector_id"] = collector_id
                new_collector: ResourceCollectorModel = ResourceCollectorModel.model_validate(data)
                session.add(new_collector)
                session.flush()
                session.refresh(new_collector)

                # Adding the items
                for item in data["resources"]:
                    # Check that the item exists, if not, ignore
                    fetched_item: ResourceModel | None = session.exec(
                        select(ResourceModel).where(ResourceModel.resource_id == item)
                    ).first()

                    if fetched_item is not None:
                        new_collector_item: ResourceCollectorMineableResourcesModel = (
                            ResourceCollectorMineableResourcesModel.model_validate(
                                {"resource_collector_id": new_collector.id, "resource_id": fetched_item.id}
                            )
                        )

                        session.add(new_collector_item)

        try:
            session.commit()

        except SQLAlchemyError:
            session.rollback()
            print("Cannot load Resource Collectors.")
            sys.exit(0)


def _populate_resources_on_planet() -> None:
    """Populate the Planet Resources tables with Resources found on the planet."""
    with Session(engine) as session:
        fetched_planets: Sequence[PlanetModel] = session.exec(select(PlanetModel)).all()

        for pp in fetched_planets:
            if len(pp.resources) == 0:
                p: Planet = Planet(tier=pp.tier)
                p.spawn_resources()

                for r in p.resources:
                    # Add the resource to the planet.
                    # If not exists
                    planet_resource: PlanetResourcesModel | None = session.exec(
                        select(PlanetResourcesModel).where(
                            PlanetResourcesModel.planet_id == pp.id,
                            PlanetResourcesModel.resource_id == r.id,
                        )
                    ).first()
                    if planet_resource is None:
                        new_planet_resource: PlanetResourcesModel = PlanetResourcesModel(
                            planet_id=pp.id,  # type: ignore[reportArgumentType]
                            resource_id=r.id,  # type: ignore[reportArgumentType]
                        )
                        session.add(new_planet_resource)
                        session.flush()

        try:
            session.commit()

        except SQLAlchemyError:
            session.rollback()
            print("Cannot load Resources on Planet.")
            sys.exit(0)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001, ANN201
    _populate_achievements()

    # Reading in necessary game config files
    _populate_resources()
    _populate_planets()
    _populate_resource_collectors()
    _populate_resources_on_planet()

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(company.router)
app.include_router(user.router)
app.include_router(shop.router)
app.include_router(achievement.router)
app.include_router(planet.router)
app.include_router(resource.router)
app.include_router(collector.router)


def main() -> None:
    """Create the database tables."""
    run("src.main:app", reload=False)
