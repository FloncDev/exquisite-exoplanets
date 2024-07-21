from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db import get_session
from src.models import (
    Experience,
    User,
    UserCreatePublic,
    UserPublic,
    UserUpdateExperience,
)

router = APIRouter()


@router.get("/user/{user_id}")
async def get_user(
    user_id: int,
    session: Session = Depends(get_session),  # noqa: B008
) -> UserPublic:
    """Endpoint to retrieve an existing user.

    :param user_id: ID of the User to retrieve.
    :param session: Database session.
    :return: a representation of the user
    """
    user = session.exec(select(User).where(User.user_id == user_id)).first()

    if user is None:
        raise HTTPException(404, "User not found")
    return user


@router.post("/user/{user_id}")
async def create_user(
    user_id: int,
    session: Session = Depends(get_session),  # noqa: B008
) -> UserCreatePublic:
    """Endpoint to register a new user.

    :param user_id: ID of the User to register.
    :param session: Database session.
    :return: id of the newly registered user
    """
    user = session.exec(select(User).where(User.user_id == user_id)).first()

    if user is None:
        user = User(user_id=user_id)
        session.add(user)
        session.commit()
    else:
        raise HTTPException(409, "User already exists")
    return UserCreatePublic(id=user_id)


@router.get("/user/{user_id}/experience")
async def get_user_experience(
    user_id: int,
    session: Session = Depends(get_session),  # noqa: B008
) -> Experience:
    """Endpoint to retrieve the given User's experience.

    :param user_id: ID of the User to retrieve.
    :param session: Database session.
    :return: Experience (an integer representing the user's experience)
    """
    user = session.exec(select(User).where(User.user_id == user_id)).first()

    if user is None:
        raise HTTPException(404, "User not found")
    return Experience(experience=user.experience)


@router.post("/user/{user_id}/experience")
async def update_user_experience(
    user_id: int,
    new_experience: UserUpdateExperience,
    session: Session = Depends(get_session),  # noqa: B008
) -> Experience:
    """Endpoint to update the given User's experience.

    :param user_id: ID of the User to update.
    :param new_experience: Represents the integer value of the user's new experience.
    :param session: Database session.
    :return: Experience (an integer representing the user's new experience)
    """
    user = session.exec(select(User).where(User.user_id == user_id)).first()

    if user is None:
        raise HTTPException(404, "User not found")
    user.experience = new_experience.new_experience
    session.add(user)
    session.commit()

    return Experience(experience=user.experience)

