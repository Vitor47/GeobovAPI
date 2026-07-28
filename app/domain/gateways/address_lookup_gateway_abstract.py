from abc import ABC, abstractmethod

from app.domain.entities.address import Address


class AddressLookupGatewayAbstract(ABC):
    """
    Abstract contract for resolving postal addresses from external providers.

    Concrete adapters (e.g. ViaCEP for Brazil) must implement this interface.
    Unsupported countries should raise UnsupportedCountryError.
    """

    @abstractmethod
    def lookup_by_postal_code(
        self,
        postal_code: str,
        country_code: str,
    ) -> Address | None:
        """
        Resolve address details for a postal code in a given country.

        Args:
            postal_code (str): Postal / ZIP code as typed by the user.
            country_code (str): ISO 3166-1 alpha-2 country code (e.g. BR).

        Returns:
            Address | None: Normalized address when found; None when the
                postal code is invalid or unknown for that country.
        """
