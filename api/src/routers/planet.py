from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.classes.planet import PlanetRepresentation
from src.db import get_session
from src.models import PlanetPublic

router = APIRouter()


@router.get("/planet/{planet_id}")
async def get_planet(planet_id: str, session: Session = Depends(get_session)) -> PlanetPublic:
    """Get the details of the given Planet."""
    return PlanetRepresentation.fetch_planet(session=session, name=planet_id).get_details()
