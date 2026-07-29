from abc import ABC, abstractmethod
from typing import Any, List, Optional, Sequence

from app.adapters.models.company import Company


class CompanyRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to Company.
    """

    @abstractmethod
    def create_company(self, data: Any, **kwargs: Any) -> Company:
        """Create a new company in the database."""

    @abstractmethod
    def get_company_by_id(
        self,
        company_id: int,
    ) -> Optional[Company]:
        """Retrieve a company by its unique ID."""

    @abstractmethod
    def get_all_companies(
        self,
    ) -> List[Company]:
        """Retrieve all companies from the database."""

    @abstractmethod
    def get_companies_by_ids(
        self,
        company_ids: Sequence[int],
    ) -> List[Company]:
        """Retrieve companies filtered by IDs."""

    @abstractmethod
    def delete_company(
        self,
        company_id: int,
    ) -> None:
        """Delete a company by its ID."""
