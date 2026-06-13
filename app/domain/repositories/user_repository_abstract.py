from abc import ABC, abstractmethod
from typing import Any, Optional

from app.adapters.models.user import User


class UserRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to User.

    This interface defines the required methods that any concrete
    user repository implementation must provide.
    """

    @abstractmethod
    def create_user(self, data: Any, **kwargs: Any) -> User:
        """
        Create a new user in the database.

        Args:
            db (Session): Active SQLAlchemy database session.
            data (Any): Object containing user data.
                        Typically a DTO instance.

        Returns:
            User: The persisted User entity instance.
        """

    @abstractmethod
    def get_user_by_id(
        self,
        user_id: int,
    ) -> Optional[User]:
        """
        Retrieve a user by its unique ID.

        Args:
            db (Session): Active SQLAlchemy database session.
            user_id (int): Unique identifier of the user.

        Returns:
            Optional[User]: The found user, or None if not found.
        """

    @abstractmethod
    def get_user_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            db (Session): Active SQLAlchemy database session.
            email (str): Unique email.

        Returns:
            Optional[User]: The found user, or None if not found.
        """

    @abstractmethod
    def delete_user(
        self,
        user_id: int,
    ) -> None:
        """
        Delete a user by its ID.

        Args:
            db (Session): Active SQLAlchemy database session.
            user_id (int): Unique identifier of the user.
        """
