from app.adapters.gateways.address.composite_address_lookup_gateway import (
    CompositeAddressLookupGateway,
    normalize_country_code,
)
from app.adapters.gateways.address.via_cep_address_lookup_gateway import (
    ViaCepAddressLookupGateway,
)
from app.adapters.gateways.address.via_cep_client import ViaCepClient


def build_address_lookup_gateway(
    client: ViaCepClient | None = None,
) -> CompositeAddressLookupGateway:
    """Wire Brazil ViaCEP today; register more country gateways here later."""
    via_cep = ViaCepAddressLookupGateway(client=client or ViaCepClient())
    return CompositeAddressLookupGateway(
        gateways_by_country={"BR": via_cep},
    )


__all__ = [
    "CompositeAddressLookupGateway",
    "ViaCepAddressLookupGateway",
    "ViaCepClient",
    "build_address_lookup_gateway",
    "normalize_country_code",
]
