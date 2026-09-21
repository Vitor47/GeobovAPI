from abc import ABC, abstractmethod
from typing import Any, Optional

from app.adapters.models.device import Device


class DeviceRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to Device.

    This interface defines the required methods that any concrete
    device repository implementation must provide.
    """

    @abstractmethod
    def create_device(self, data: Any, **kwargs: Any) -> Device:
        """
        Create a new LoRa GPS device linked to a cattle and company.

        Args:
            db (Session): Active SQLAlchemy database session.
            data (Any): Object containing device data.
                        Typically a DTO instance.

        Returns:
            Device: The persisted Device entity instance.
        """

    @abstractmethod
    def get_device_by_id_and_company_id(
        self,
        device_id: int,
        company_id: int,
    ) -> Optional[Device]:
        """
        Retrieve a device by ID and company ID.

        Args:
            db (Session): Active SQLAlchemy database session.
            device_id (int): Unique identifier of the device.
            company_id (int): Identifier of the owning company.

        Returns:
            Optional[Device]: The found record, or None if not found.
        """

    @abstractmethod
    def get_devices_by_company_id(
        self,
        company_id: int,
    ) -> list[Device]:
        """
        Retrieve all devices associated with a given company.

        Args:
            db (Session): Active SQLAlchemy database session.
            company_id (int): Identifier of the company.

        Returns:
            list[Device]: List of devices for the company.
        """

    @abstractmethod
    def get_active_device_by_serial_and_company(
        self,
        serial_number: str,
        company_id: int,
    ) -> Optional[Device]:
        """
        Retrieve an active collar device by serial number within a company.

        Args:
            serial_number (str): Physical device serial.
            company_id (int): Company owning the gateway and device.

        Returns:
            Optional[Device]: The found record, or None if not found.
        """

    @abstractmethod
    def get_active_device_by_cattle_and_company(
        self,
        cattle_id: int,
        company_id: int,
    ) -> Optional[Device]:
        """
        Retrieve an active collar device linked to a cattle within a company.

        Used by gateway ingest to update last_seen when telemetry is
        associated by cow_id.

        Args:
            cattle_id (int): Cattle identifier from the LoRa packet (cow_id).
            company_id (int): Company owning the gateway and device.

        Returns:
            Optional[Device]: The found record, or None if not found.
        """

    @abstractmethod
    def update_last_seen(self, device_id: int) -> None:
        """
        Update the last_seen_at timestamp for a device.

        Args:
            db (Session): Active SQLAlchemy database session.
            device_id (int): Unique identifier of the device.

        Returns:
            None
        """
