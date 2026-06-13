from abc import ABC, abstractmethod
from typing import Any, List, Optional

from app.adapters.models.company import Company


class CompanyRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to Company.

    This interface defines the required methods that any concrete
    company repository implementation must provide.
    """

    @abstractmethod
    def create_company(self, data: Any, **kwargs: Any) -> Company:
        """
        Create a new company in the database.

        Args:
            db (Session): Active SQLAlchemy database session.
            data (Any): Object containing company data.
                        Typically a DTO instance.

        Returns:
            Company: The persisted Company entity instance.
        """

    @abstractmethod
    def get_company_by_id(
        self,
        company_id: int,
    ) -> Optional[Company]:
        """
        Retrieve a company by its unique ID.

        Args:
            db (Session): Active SQLAlchemy database session.
            company_id (int): Unique identifier of the company.

        Returns:
            Optional[Company]: The found company, or None if not found.
        """

    @abstractmethod
    def get_all_companies(
        self,
    ) -> List[Company]:
        """
        Retrieve all companies from the database.

        Args:
            db (Session): Active SQLAlchemy database session.

        Returns:
            List[Company]: List of all companies.
        """

    @abstractmethod
    def delete_company(
        self,
        company_id: int,
    ) -> None:
        """
        Delete a company by its ID.

        Args:
            db (Session): Active SQLAlchemy database session.
            company_id (int): Unique identifier of the company.
        """
