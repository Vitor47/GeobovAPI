import pytest

from app.adapters.gateways.address.composite_address_lookup_gateway import (
    CompositeAddressLookupGateway,
    normalize_country_code,
)
from app.adapters.gateways.address.via_cep_address_lookup_gateway import (
    ViaCepAddressLookupGateway,
)
from app.domain.entities.address import Address
from app.domain.exceptions.address import UnsupportedCountryError


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Brazil", "BR"),
        ("brasil", "BR"),
        ("BR", "BR"),
        ("bra", "BR"),
        ("", None),
        (None, None),
        ("US", None),
    ],
)
def test_normalize_country_code_maps_brazil_aliases(raw, expected):
    assert normalize_country_code(raw) == expected


@pytest.mark.unit
def test_via_cep_gateway_returns_address_when_client_responds(mocker):
    client = mocker.Mock()
    client.fetch_by_cep.return_value = {
        "cep": "01310-100",
        "logradouro": "Avenida Paulista",
        "bairro": "Bela Vista",
        "localidade": "São Paulo",
        "uf": "SP",
    }
    gateway = ViaCepAddressLookupGateway(client=client)

    address = gateway.lookup_by_postal_code("01310-100", "BR")

    assert address is not None
    assert address.city == "São Paulo"
    client.fetch_by_cep.assert_called_once_with("01310100")


@pytest.mark.unit
def test_via_cep_gateway_raises_unsupported_country(mocker):
    gateway = ViaCepAddressLookupGateway(client=mocker.Mock())

    with pytest.raises(UnsupportedCountryError):
        gateway.lookup_by_postal_code("01310-100", "US")


@pytest.mark.unit
def test_composite_gateway_routes_brazil_and_rejects_unknown(mocker):
    brazil = mocker.Mock()
    brazil.lookup_by_postal_code.return_value = Address(
        street="Rua A",
        city="Curitiba",
        state="PR",
        postal_code="80010-000",
        country_code="BR",
    )
    composite = CompositeAddressLookupGateway(gateways_by_country={"BR": brazil})

    found = composite.lookup_by_postal_code("80010-000", "Brazil")
    assert found is not None
    assert found.city == "Curitiba"
    brazil.lookup_by_postal_code.assert_called_once_with("80010-000", "BR")

    with pytest.raises(UnsupportedCountryError):
        composite.lookup_by_postal_code("10001", "US")
