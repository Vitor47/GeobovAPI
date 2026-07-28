import pytest

from app.application.dtos.address_dto import AddressLookupRequestDTO
from app.application.steps.address.lookup_address_step import LookupAddressStep
from app.application.use_cases.address.lookup_address_use_case import (
    LookupAddressUseCase,
)
from app.domain.entities.address import Address


@pytest.mark.unit
def test_lookup_address_step_sets_response_dto_when_gateway_finds_address(mocker):
    gateway = mocker.Mock()
    gateway.lookup_by_postal_code.return_value = Address(
        street="Praça da Sé",
        city="São Paulo",
        state="SP",
        postal_code="01001-000",
        country_code="BR",
        neighborhood="Sé",
    )
    use_case = LookupAddressUseCase(
        gateway=gateway,
        payload=AddressLookupRequestDTO(postal_code="01001-000", country="BR"),
    )

    LookupAddressStep(use_case=use_case).run()

    assert use_case.data is not None
    assert use_case.data.city == "São Paulo"
    assert use_case.data.address_line == "Praça da Sé, Sé"
    gateway.lookup_by_postal_code.assert_called_once_with(
        postal_code="01001-000",
        country_code="BR",
    )


@pytest.mark.unit
def test_lookup_address_step_sets_none_when_gateway_returns_none(mocker):
    gateway = mocker.Mock()
    gateway.lookup_by_postal_code.return_value = None
    use_case = LookupAddressUseCase(
        gateway=gateway,
        payload=AddressLookupRequestDTO(postal_code="00000-000", country="BR"),
    )

    LookupAddressStep(use_case=use_case).run()

    assert use_case.data is None
