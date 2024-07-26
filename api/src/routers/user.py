from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.db import get_session
from src.models import (
    Experience,
    User,
    UserAddExperience,
    UserCreatePublic,
    UserExperienceReturn,
    UserPublic,
    UserSetExperience,
)

router = APIRouter()


@router.get("/user/{user_id}")
async def get_user(
    user_id: str,
    session: Session = Depends(get_session),
) -> UserPublic:
    """Endpoint to retrieve an existing user.

    :param user_id: ID of the User to retrieve.
    :param session: Database session.
    :return: a representation of the user
    """
    user = session.exec(select(User).where(User.user_id == user_id)).first()

    if user is None:
        raise HTTPException(404, "User not found")
    return UserPublic(
        user_id=user_id,
        experience=Experience(level=Experience.level_from_experience(user.experience), experience=user.experience),
    )


@router.post("/user/{user_id}")
async def create_user(
    user_id: str,
    session: Session = Depends(get_session),
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


@router.patch("/user/{user_id}/experience/add")
async def add_user_experience(
    user_id: str,
    new_experience: UserAddExperience,
    session: Session = Depends(get_session),
) -> UserExperienceReturn:
    """Endpoint to add to the given User's experience.

    :param user_id: ID of the User to retrieve.
    :param session: Database session.
    :return: Experience (an integer representing the user's experience)
    """
    user = session.exec(select(User).where(User.user_id == user_id)).first()

    if user is None:
        raise HTTPException(404, "User not found")

    current_level = Experience.level_from_experience(user.experience)

    user.experience += new_experience.experience
    session.add(user)
    session.commit()

    new_level = Experience.level_from_experience(user.experience)
    levelled_up = current_level < new_level

    return UserExperienceReturn(level_up=levelled_up, new_level=new_level, new_experience=user.experience)


@router.post("/user/{user_id}/experience/set")
async def set_user_experience(
    user_id: str,
    new_experience: UserSetExperience,
    session: Session = Depends(get_session),
) -> UserExperienceReturn:
    """Endpoint to set the given User's experience.

    :param user_id: ID of the User to update.
    :param new_experience: Represents the integer value of the user's new experience.
    :param session: Database session.
    :return: Experience (an integer representing the user's new experience)
    """
    user = session.exec(select(User).where(User.user_id == user_id)).first()

    if user is None:
        raise HTTPException(404, "User not found")

    current_level = Experience.level_from_experience(user.experience)

    user.experience = new_experience.experience
    session.add(user)
    session.commit()

    new_level = Experience.level_from_experience(user.experience)
    levelled_up = current_level < new_level

    return UserExperienceReturn(level_up=levelled_up, new_level=new_level, new_experience=user.experience)
