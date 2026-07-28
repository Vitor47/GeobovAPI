from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from app.domain.entities.cattle_data import CattleData


class CattleDataRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to cattle telemetry.

    Concrete implementations store high-frequency samples and downsampled
    history documents (e.g. MongoDB collections).
    """

    @abstractmethod
    def create_cattle_data(self, data: Any) -> CattleData:
        """
        Persist a new high-frequency telemetry sample.

        Args:
            data (Any): Object containing cattle telemetry fields.
                        Typically a CattleDataCreateDTO instance.

        Returns:
            CattleData: The persisted telemetry entity.
        """

    @abstractmethod
    def get_cattle_data_by_id_and_company_id(
        self,
        telemetry_id: str,
        company_id: int,
    ) -> Optional[CattleData]:
        """
        Retrieve a telemetry record by ID scoped to a company.

        Searches both raw and history collections.

        Args:
            telemetry_id (str): Unique identifier of the telemetry document.
            company_id (int): Identifier of the owning company.

        Returns:
            Optional[CattleData]: The found record, or None if not found.
        """

    @abstractmethod
    def get_cattle_data_by_company_id(
        self,
        company_id: int,
    ) -> list[CattleData]:
        """
        Retrieve telemetry records associated with a given company.

        Returns raw samples and history documents for the tenant.

        Args:
            company_id (int): Identifier of the company.

        Returns:
            list[CattleData]: List of telemetry records for the company.
        """

    @abstractmethod
    def ensure_indexes(self) -> None:
        """
        Create indexes required for tenant-scoped queries and downsampling.

        Returns:
            None: Indexes are created as a side effect.
        """

    @abstractmethod
    def downsample_raw_telemetry(
        self,
        older_than: datetime,
        interval_minutes: int,
    ) -> int:
        """
        Aggregate raw samples older than a cutoff into history buckets and
        delete the original high-frequency documents.

        Args:
            older_than (datetime): Cutoff timestamp; samples before this
                are downsampled.
            interval_minutes (int): History bucket size in minutes.

        Returns:
            int: Number of raw documents deleted after aggregation.
        """
