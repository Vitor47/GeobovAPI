from __future__ import annotations

from app.domain.entities.address import Address
from app.domain.exceptions.address import UnsupportedCountryError
from app.domain.gateways.address_lookup_gateway_abstract import (
    AddressLookupGatewayAbstract,
)

# Aliases accepted from admin forms before routing to a country gateway.
_COUNTRY_ALIASES: dict[str, str] = {
    "BR": "BR",
    "BRA": "BR",
    "BRAZIL": "BR",
    "BRASIL": "BR",
}


def normalize_country_code(country: str | None) -> str | None:
    """
    Normalize free-text country input to ISO 3166-1 alpha-2 when known.

    Args:
        country: Raw country value from forms (e.g. Brazil, BR, Brasil).

    Returns:
        Normalized alpha-2 code, or None when empty / unknown.
    """
    if country is None:
        return None
    key = country.strip().upper()
    if not key:
        return None
    return _COUNTRY_ALIASES.get(key)


class CompositeAddressLookupGateway(AddressLookupGatewayAbstract):
    """
    Routes postal-code lookup to a country-specific gateway.

    New countries can be registered later without changing callers.
    """

    def __init__(
        self,
        gateways_by_country: dict[str, AddressLookupGatewayAbstract],
    ) -> None:
        self._gateways_by_country = {
            code.upper(): gateway for code, gateway in gateways_by_country.items()
        }

    def lookup_by_postal_code(
        self,
        postal_code: str,
        country_code: str,
    ) -> Address | None:
        normalized = (
            normalize_country_code(country_code) or country_code.strip().upper()
        )
        gateway = self._gateways_by_country.get(normalized)
        if gateway is None:
            raise UnsupportedCountryError(normalized)
        return gateway.lookup_by_postal_code(postal_code, normalized)
