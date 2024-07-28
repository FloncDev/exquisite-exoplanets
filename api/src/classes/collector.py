from typing import Any, Self

from fastapi import HTTPException
from sqlmodel import Session, select
from src.models import ResourceCollectorModel, ResourceCollectorPublic


class ResourceCollectorRepresentation:
    """Class representing a collector from the database."""

    def __init__(self, session: Session, collector: ResourceCollectorModel) -> None:
        self.session: Session = session
        self.collector: ResourceCollectorModel = collector

    @classmethod
    def fetch_collector(cls, session: Session, name: str) -> Self:
        """Fetch a planet from the database. Return class with fetched planet."""
        fetched_collector: ResourceCollectorModel | None = session.exec(
            select(ResourceCollectorModel).where(ResourceCollectorModel.collector_id == name)).first()

        if fetched_collector is None:
            raise HTTPException(status_code=404, detail="Collector not found.")

        return cls(session=session, collector=fetched_collector)

    def get_collector(self) -> ResourceCollectorModel:
        """Get the Collector model bound to the instance."""
        return self.collector

    def get_details(self) -> ResourceCollectorPublic:
        """Get the details of the Planet."""
        data: dict[str, Any] = dict(self.collector)
        data["mineable_resources"] = [r.resource.resource_id for r in self.collector.mineable_resources]
        return ResourceCollectorPublic.model_validate(data)
