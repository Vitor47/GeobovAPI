import pytest

from app.application.dtos.device_dto import DeviceCreateDTO
from app.application.steps.device.create_device_step import CreateDeviceStep
from app.application.use_cases.device.create_device_use_case import (
    CreateDeviceUseCase,
)


@pytest.fixture
def device_create_payload() -> DeviceCreateDTO:
    return DeviceCreateDTO(
        serial_number="LORA-001",
        cattle_id=1,
        company_id=1,
        name="GPS Collar 1",
    )


@pytest.fixture
def mock_device_record():
    from unittest.mock import Mock

    record = Mock()
    record.id = 1
    record.serial_number = "LORA-001"
    record.name = "GPS Collar 1"
    record.cattle_id = 1
    record.company_id = 1
    record.api_key = "test-api-key"
    record.is_active = True
    record.transmission_interval_minutes = 5
    record.last_seen_at = None
    return record


@pytest.mark.unit
def test_create_device_step_sets_response_dto_when_device_is_created(
    device_create_payload, mock_device_record, mocker
):
    mock_repository = mocker.Mock()
    mock_repository.create_device.return_value = mock_device_record

    use_case = CreateDeviceUseCase(
        repository=mock_repository,
        payload=device_create_payload,
    )

    CreateDeviceStep(use_case=use_case).run()

    assert use_case.data.serial_number == "LORA-001"
    assert use_case.data.api_key == "test-api-key"
    mock_repository.create_device.assert_called_once_with(device_create_payload)
