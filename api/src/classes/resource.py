from typing import Self

from fastapi import HTTPException
from sqlmodel import Session, select
from src.models import ResourceModel, ResourcePublic


class ResourceRepresentation:
    """Class representing a Resource from the database."""

    def __init__(self, session: Session, resource: ResourceModel) -> None:
        self.session: Session = session
        self.resource: ResourceModel = resource

    @classmethod
    def fetch_resource(cls, session: Session, name: str) -> Self:
        """Fetch a planet from the database. Return class with fetched planet."""
        fetched_resource: ResourceModel | None = session.exec(
            select(ResourceModel).where(ResourceModel.resource_id == name)
        ).first()

        if fetched_resource is None:
            raise HTTPException(status_code=404, detail="Resource not found.")

        return cls(session=session, resource=fetched_resource)

    def get_resource(self) -> ResourceModel:
        """Get the Resource model bound to the instance."""
        return self.resource

    def get_details(self) -> ResourcePublic:
        """Get the details of the Planet."""
        data = dict(self.resource)
        data["found_on"] = [p.planet.planet_id for p in self.resource.on_planets]
        return ResourcePublic.model_validate(data)
