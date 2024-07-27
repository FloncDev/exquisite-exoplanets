from typing import Self

from fastapi import HTTPException
from sqlmodel import Session, select
from src.models import Experience, User, UserPublic


class UserRepresentation:
    """Class representing a `user` in the database."""

    def __init__(self, session: Session, user: User) -> None:
        self.session: Session = session
        self.user: User = user

    @classmethod
    def fetch_user(cls, session: Session, user_id: str) -> Self:
        """Fetch the given User from the database.

        :param session: Database session.
        :param user_id: ID of the User to fetch.
        :return: Instance bound with the fetched User.
        """
        fetched_user: User | None = session.exec(select(User).where(User.user_id == user_id)).first()

        if fetched_user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        return cls(session=session, user=fetched_user)

    def get_user(self) -> User:
        """Get the User model bound to the instance.

        :return: Bound User model.
        """
        return self.user

    def get_details(self) -> UserPublic:
        """Get the details of the User.

        :return: User details.
        """
        return UserPublic(
            user_id=self.user.user_id,
            experience=Experience(
                level=Experience.level_from_experience(self.user.experience), experience=self.user.experience
            ),
        )
