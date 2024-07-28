from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.classes.collector import ResourceCollectorRepresentation
from src.db import get_session
from src.models import ResourceCollectorPublic

router = APIRouter()


@router.get("/collector/{collector_id}")
async def get_collector(collector_id: str, session: Session = Depends(get_session)) -> ResourceCollectorPublic:
    """Get the details of the given Planet."""
    return ResourceCollectorRepresentation.fetch_collector(session=session, name=collector_id).get_details()
