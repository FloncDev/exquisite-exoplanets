from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.classes.resource import ResourceRepresentation
from src.db import get_session
from src.models import ResourcePublic

router = APIRouter()


@router.get("/resource/{resource_id}")
async def get_resource(resource_id: str, session: Session = Depends(get_session)) -> ResourcePublic:
    """Get the details of the given Planet."""
    return ResourceRepresentation.fetch_resource(session=session, name=resource_id).get_details()
