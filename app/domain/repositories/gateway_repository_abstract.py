from abc import ABC, abstractmethod
from typing import Any, Optional

from app.adapters.models.gateway import Gateway


class GatewayRepositoryAbstract(ABC):
    """
    Abstract contract for persistence operations related to LoRa Gateway.

    This interface defines the required methods that any concrete
    gateway repository implementation must provide.
    """

    @abstractmethod
    def create_gateway(self, data: Any, **kwargs: Any) -> Gateway:
        """
        Create a new LoRa gateway for a company.

        Args:
            db (Session): Active SQLAlchemy database session.
            data (Any): Object containing gateway data.
                        Typically a DTO instance.

        Returns:
            Gateway: The persisted Gateway entity instance.
        """

    @abstractmethod
    def get_gateway_by_id_and_company_id(
        self,
        gateway_id: int,
        company_id: int,
    ) -> Optional[Gateway]:
        """
        Retrieve a gateway by ID and company ID.

        Args:
            db (Session): Active SQLAlchemy database session.
            gateway_id (int): Unique identifier of the gateway.
            company_id (int): Identifier of the owning company.

        Returns:
            Optional[Gateway]: The found record, or None if not found.
        """

    @abstractmethod
    def get_gateways_by_company_id(
        self,
        company_id: int,
    ) -> list[Gateway]:
        """
        Retrieve all gateways associated with a given company.

        Args:
            db (Session): Active SQLAlchemy database session.
            company_id (int): Identifier of the company.

        Returns:
            list[Gateway]: List of gateways for the company.
        """

    @abstractmethod
    def get_gateway_by_api_key(
        self,
        api_key: str,
    ) -> Optional[Gateway]:
        """
        Retrieve an active gateway by its API key for telemetry ingestion.

        Args:
            db (Session): Active SQLAlchemy database session.
            api_key (str): Gateway authentication key.

        Returns:
            Optional[Gateway]: The found record, or None if not found.
        """

    @abstractmethod
    def update_last_seen(self, gateway_id: int) -> None:
        """
        Update the last_seen_at timestamp for a gateway.

        Args:
            db (Session): Active SQLAlchemy database session.
            gateway_id (int): Unique identifier of the gateway.

        Returns:
            None
        """
