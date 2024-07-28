from typing import Self

from fastapi import HTTPException
from sqlmodel import Session, select
from src.models import PlanetModel, PlanetPublic


class PlanetRepresentation:
    """Class representing a Planet from the database."""

    def __init__(self, session: Session, planet: PlanetModel) -> None:
        self.session: Session = session
        self.planet: PlanetModel = planet

    @classmethod
    def fetch_planet(cls, session: Session, name: str) -> Self:
        """Fetch a planet from the database. Return class with fetched planet."""
        fetched_planet: PlanetModel | None = session.exec(
            select(PlanetModel).where(PlanetModel.planet_id == name)).first()

        if fetched_planet is None:
            raise HTTPException(status_code=404, detail="Planet not found.")

        return cls(session=session, planet=fetched_planet)

    def get_planet(self) -> PlanetModel:
        """Get the Planet model bound to the instance."""
        return self.planet

    def get_details(self) -> PlanetPublic:
        """Get the details of the Planet."""
        data = dict(self.planet)
        data["available_resources"] = [r.resource.resource_id for r in self.planet.resources]
        return PlanetPublic.model_validate(data)
