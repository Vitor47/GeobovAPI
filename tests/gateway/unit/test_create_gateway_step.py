import pytest

from app.application.dtos.gateway_dto import GatewayCreateDTO
from app.application.steps.gateway.create_gateway_step import CreateGatewayStep
from app.application.use_cases.gateway.create_gateway_use_case import (
    CreateGatewayUseCase,
)


@pytest.fixture
def gateway_create_payload() -> GatewayCreateDTO:
    return GatewayCreateDTO(
        serial_number="GW-001",
        company_id=1,
        name="Barn receiver",
    )


@pytest.mark.unit
def test_create_gateway_step_sets_response_dto_with_api_key(
    gateway_create_payload, mocker
):
    record = mocker.Mock()
    record.id = 1
    record.serial_number = "GW-001"
    record.name = "Barn receiver"
    record.company_id = 1
    record.api_key = "gateway-secret"
    record.is_active = True
    record.last_seen_at = None

    mock_repository = mocker.Mock()
    mock_repository.create_gateway.return_value = record

    use_case = CreateGatewayUseCase(
        repository=mock_repository,
        payload=gateway_create_payload,
    )

    CreateGatewayStep(use_case=use_case).run()

    assert use_case.data.serial_number == "GW-001"
    assert use_case.data.api_key == "gateway-secret"
    mock_repository.create_gateway.assert_called_once_with(gateway_create_payload)
