import pytest

from app.adapters.gateways.address.via_cep_acl import (
    format_brazilian_cep,
    map_via_cep_response,
    normalize_brazilian_cep,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("01001-000", "01001000"),
        ("01001000", "01001000"),
        ("01.001-000", "01001000"),
        ("123", None),
        ("", None),
    ],
)
def test_normalize_brazilian_cep_when_input_varies(raw, expected):
    assert normalize_brazilian_cep(raw) == expected


@pytest.mark.unit
def test_format_brazilian_cep_inserts_hyphen():
    assert format_brazilian_cep("01001000") == "01001-000"


@pytest.mark.unit
def test_map_via_cep_response_returns_address_when_payload_is_valid():
    payload = {
        "cep": "01001-000",
        "logradouro": "Praça da Sé",
        "bairro": "Sé",
        "localidade": "São Paulo",
        "uf": "SP",
    }

    address = map_via_cep_response(payload)

    assert address is not None
    assert address.street == "Praça da Sé"
    assert address.neighborhood == "Sé"
    assert address.city == "São Paulo"
    assert address.state == "SP"
    assert address.postal_code == "01001-000"
    assert address.country_code == "BR"
    assert address.to_address_line() == "Praça da Sé, Sé"


@pytest.mark.unit
def test_map_via_cep_response_returns_none_when_erro_flag_is_true():
    assert map_via_cep_response({"erro": True}) is None


@pytest.mark.unit
def test_map_via_cep_response_returns_none_when_city_is_missing():
    assert map_via_cep_response({"cep": "01001-000", "localidade": ""}) is None
