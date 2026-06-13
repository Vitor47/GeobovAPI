from abc import ABC, abstractmethod
from typing import Any, Optional

from app.adapters.models.cattle import CattleData


class CattleRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to CattleData.

    This interface defines the required methods that any concrete
    cattle repository implementation must provide.
    """

    @abstractmethod
    def create_cattle(self, data: Any, **kwargs: Any) -> CattleData:
        """
        Create a new cattle record in the database.

        Args:
            db (Session): Active SQLAlchemy database session.
            data (Any): Object containing cattle data.
                        Typically a DTO instance.

        Returns:
            CattleData: The persisted CattleData entity instance.
        """

    @abstractmethod
    def get_cattle_by_id_and_company_id(
        self,
        cattle_id: int,
        company_id: int,
    ) -> Optional[CattleData]:
        """
        Retrieve a cattle record by cattle ID and company ID.

        Args:
            db (Session): Active SQLAlchemy database session.
            cattle_id (int): Unique identifier of the cattle data record.
            company_id (int): Identifier of the owning company.

        Returns:
            Optional[CattleData]: The found record, or None if not found.
        """

    @abstractmethod
    def get_cattles_by_company_id(
        self,
        company_id: int,
    ) -> list[CattleData]:
        """
        Retrieve all cattle records associated with a given company.

        Args:
            db (Session): Active SQLAlchemy database session.
            company_id (int): Identifier of the company.

        Returns:
            list[CattleData]: List of cattle records for the company.
        """
