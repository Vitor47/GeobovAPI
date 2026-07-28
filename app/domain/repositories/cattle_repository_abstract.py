from abc import ABC, abstractmethod
from typing import Any, Optional

from app.adapters.models.cattle import Cattle


class CattleRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to Cattle animals.

    This interface defines the required methods that any concrete
    cattle repository implementation must provide.
    """

    @abstractmethod
    def create_cattle(self, data: Any) -> Cattle:
        """
        Create a new cattle animal record for a company.

        Args:
            data (Any): Object containing cattle fields.
                        Typically a CattleCreateDTO instance.

        Returns:
            Cattle: The persisted Cattle entity instance.
        """

    @abstractmethod
    def get_cattle_by_id_and_company_id(
        self,
        cattle_id: int,
        company_id: int,
    ) -> Optional[Cattle]:
        """
        Retrieve a cattle animal by ID scoped to a company.

        Args:
            cattle_id (int): Unique identifier of the cattle.
            company_id (int): Identifier of the owning company.

        Returns:
            Optional[Cattle]: The found record, or None if not found.
        """

    @abstractmethod
    def get_cattles_by_company_id(
        self,
        company_id: int,
    ) -> list[Cattle]:
        """
        Retrieve all cattle animals associated with a given company.

        Args:
            company_id (int): Identifier of the company.

        Returns:
            list[Cattle]: List of cattle for the company.
        """

    @abstractmethod
    def update_cattle(self, cattle_id: int, company_id: int, data: Any) -> Cattle:
        """
        Update mutable cattle fields scoped to a company.

        Args:
            cattle_id (int): Unique identifier of the cattle.
            company_id (int): Identifier of the owning company.
            data (Any): Object containing fields to update.
                        Typically a CattleUpdateDTO instance.

        Returns:
            Cattle: The updated Cattle entity instance.
        """
