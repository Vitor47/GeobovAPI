from __future__ import annotations

from app.adapters.gateways.address.via_cep_acl import (
    map_via_cep_response,
    normalize_brazilian_cep,
)
from app.adapters.gateways.address.via_cep_client import ViaCepClient
from app.domain.entities.address import Address
from app.domain.exceptions.address import UnsupportedCountryError
from app.domain.gateways.address_lookup_gateway_abstract import (
    AddressLookupGatewayAbstract,
)

_SUPPORTED_COUNTRY = "BR"


class ViaCepAddressLookupGateway(AddressLookupGatewayAbstract):
    """
    Brazil-only address lookup via ViaCEP.

    Acts as the adapter behind AddressLookupGatewayAbstract; ACL mapping
    lives in ``via_cep_acl`` so ViaCEP field names never leak into domain.
    """

    def __init__(self, client: ViaCepClient | None = None) -> None:
        self._client = client or ViaCepClient()

    def lookup_by_postal_code(
        self,
        postal_code: str,
        country_code: str,
    ) -> Address | None:
        normalized_country = country_code.strip().upper()
        if normalized_country != _SUPPORTED_COUNTRY:
            raise UnsupportedCountryError(normalized_country)

        digits = normalize_brazilian_cep(postal_code)
        if digits is None:
            return None

        payload = self._client.fetch_by_cep(digits)
        if payload is None:
            return None

        return map_via_cep_response(payload)
