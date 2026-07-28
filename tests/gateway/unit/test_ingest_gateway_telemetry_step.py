from unittest.mock import Mock

import pytest

from app.application.dtos.gateway_dto import GatewayTelemetryIngestDTO
from app.application.steps.gateway.ingest_gateway_telemetry_step import (
    IngestGatewayTelemetryStep,
)
from app.application.use_cases.gateway.ingest_gateway_telemetry_use_case import (
    IngestGatewayTelemetryUseCase,
)
from app.domain.use_cases.exceptions import StopUseCaseException


@pytest.fixture
def ingest_payload() -> GatewayTelemetryIngestDTO:
    return GatewayTelemetryIngestDTO(
        device_serial="LORA-COLLAR-001",
        lat=-23.55,
        lon=-46.63,
    )


@pytest.mark.unit
def test_ingest_gateway_telemetry_resolves_device_and_creates_cattle_data(
    ingest_payload, mocker
):
    mock_gateway = Mock()
    mock_gateway.id = 5
    mock_gateway.company_id = 1

    mock_device = Mock()
    mock_device.id = 1
    mock_device.cattle_id = 10
    mock_device.company_id = 1

    mock_cattle_data = Mock()
    mock_cattle_data.id = "507f1f77bcf86cd799439011"
    mock_cattle_data.lat = -23.55
    mock_cattle_data.lon = -46.63

    mock_gateway_repo = mocker.Mock()
    mock_gateway_repo.get_gateway_by_api_key.return_value = mock_gateway

    mock_device_repo = mocker.Mock()
    mock_device_repo.get_active_device_by_serial_and_company.return_value = mock_device

    mock_cattle_data_repo = mocker.Mock()
    mock_cattle_data_repo.create_cattle_data.return_value = mock_cattle_data

    use_case = IngestGatewayTelemetryUseCase(
        gateway_repository=mock_gateway_repo,
        device_repository=mock_device_repo,
        cattle_data_repository=mock_cattle_data_repo,
        api_key="gateway-key",
        payload=ingest_payload,
    )

    IngestGatewayTelemetryStep(use_case=use_case).run()

    assert use_case.data.gateway_id == 5
    assert use_case.data.device_id == 1
    assert use_case.data.cattle_data_id == "507f1f77bcf86cd799439011"
    mock_device_repo.get_active_device_by_serial_and_company.assert_called_once_with(
        serial_number="LORA-COLLAR-001",
        company_id=1,
    )
    mock_device_repo.update_last_seen.assert_called_once_with(1)
    mock_gateway_repo.update_last_seen.assert_called_once_with(5)


@pytest.mark.unit
def test_ingest_raises_when_gateway_api_key_is_invalid(ingest_payload, mocker):
    mock_gateway_repo = mocker.Mock()
    mock_gateway_repo.get_gateway_by_api_key.return_value = None

    use_case = IngestGatewayTelemetryUseCase(
        gateway_repository=mock_gateway_repo,
        device_repository=mocker.Mock(),
        cattle_data_repository=mocker.Mock(),
        api_key="bad-key",
        payload=ingest_payload,
    )

    with pytest.raises(StopUseCaseException, match="Invalid or inactive gateway"):
        IngestGatewayTelemetryStep(use_case=use_case).run()


@pytest.mark.unit
def test_ingest_raises_when_device_serial_is_unknown(ingest_payload, mocker):
    mock_gateway = Mock()
    mock_gateway.id = 5
    mock_gateway.company_id = 1

    mock_gateway_repo = mocker.Mock()
    mock_gateway_repo.get_gateway_by_api_key.return_value = mock_gateway

    mock_device_repo = mocker.Mock()
    mock_device_repo.get_active_device_by_serial_and_company.return_value = None

    use_case = IngestGatewayTelemetryUseCase(
        gateway_repository=mock_gateway_repo,
        device_repository=mock_device_repo,
        cattle_data_repository=mocker.Mock(),
        api_key="gateway-key",
        payload=ingest_payload,
    )

    with pytest.raises(StopUseCaseException, match="Unknown or inactive device"):
        IngestGatewayTelemetryStep(use_case=use_case).run()
