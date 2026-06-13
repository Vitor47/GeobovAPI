import pytest

from app.application.dtos.device_dto import DeviceTelemetryIngestDTO
from app.application.steps.device.ingest_telemetry_step import (
    IngestTelemetryStep,
)
from app.application.use_cases.device.ingest_telemetry_use_case import (
    IngestTelemetryUseCase,
)
from app.domain.use_cases.exceptions import StopUseCaseException


@pytest.fixture
def telemetry_payload() -> DeviceTelemetryIngestDTO:
    return DeviceTelemetryIngestDTO(
        lat=-23.55,
        lon=-46.63,
        movement=0.5,
        temperature=38.5,
    )


@pytest.mark.unit
def test_ingest_telemetry_step_creates_cattle_data_and_updates_device(
    telemetry_payload, mocker
):
    from unittest.mock import Mock

    mock_device = Mock()
    mock_device.id = 1
    mock_device.cattle_id = 10
    mock_device.company_id = 1

    mock_cattle_data = Mock()
    mock_cattle_data.id = 100
    mock_cattle_data.lat = -23.55
    mock_cattle_data.lon = -46.63
    mock_cattle_data.movement = 0.5
    mock_cattle_data.temperature = 38.5

    mock_device_repo = mocker.Mock()
    mock_device_repo.get_device_by_api_key.return_value = mock_device

    mock_cattle_repo = mocker.Mock()
    mock_cattle_repo.create_cattle.return_value = mock_cattle_data

    use_case = IngestTelemetryUseCase(
        device_repository=mock_device_repo,
        cattle_repository=mock_cattle_repo,
        api_key="valid-key",
        payload=telemetry_payload,
    )

    IngestTelemetryStep(use_case=use_case).run()

    assert use_case.data.cattle_data_id == 100
    assert use_case.data.device_id == 1
    mock_device_repo.update_last_seen.assert_called_once_with(1)
    mock_cattle_repo.create_cattle.assert_called_once()


@pytest.mark.unit
def test_ingest_telemetry_step_raises_when_device_is_invalid(telemetry_payload, mocker):
    mock_device_repo = mocker.Mock()
    mock_device_repo.get_device_by_api_key.return_value = None

    use_case = IngestTelemetryUseCase(
        device_repository=mock_device_repo,
        cattle_repository=mocker.Mock(),
        api_key="invalid-key",
        payload=telemetry_payload,
    )

    with pytest.raises(StopUseCaseException):
        IngestTelemetryStep(use_case=use_case).run()
