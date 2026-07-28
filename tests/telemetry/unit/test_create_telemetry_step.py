from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.application.dtos.cattle_data_dto import CattleDataCreateDTO
from app.application.steps.telemetry.create_telemetry_step import CreateTelemetryStep
from app.application.use_cases.telemetry.create_telemetry_use_case import (
    CreateTelemetryUseCase,
)
from app.domain.use_cases.exceptions import StopUseCaseException


@pytest.fixture
def telemetry_create_payload() -> CattleDataCreateDTO:
    return CattleDataCreateDTO(
        cattle_id=1,
        lat=-23.55,
        lon=-46.63,
        company_id=1,
    )


@pytest.fixture
def mock_telemetry_record():
    record = Mock()
    record.id = "507f1f77bcf86cd799439011"
    record.cattle_id = 1
    record.lat = -23.55
    record.lon = -46.63
    record.timestamp = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc)
    return record


@pytest.mark.unit
def test_create_telemetry_step_sets_response_dto_when_record_is_created(
    telemetry_create_payload, mock_telemetry_record, mocker
):
    mock_repository = mocker.Mock()
    mock_repository.create_cattle_data.return_value = mock_telemetry_record
    mock_cattle_repository = mocker.Mock()
    mock_cattle_repository.get_cattle_by_id_and_company_id.return_value = Mock(id=1)

    use_case = CreateTelemetryUseCase(
        repository=mock_repository,
        cattle_repository=mock_cattle_repository,
        payload=telemetry_create_payload,
    )

    CreateTelemetryStep(use_case=use_case).run()

    assert use_case.data.id == "507f1f77bcf86cd799439011"
    assert use_case.data.cattle_id == 1
    assert use_case.data.lat == -23.55
    assert use_case.data.lon == -46.63
    mock_repository.create_cattle_data.assert_called_once_with(telemetry_create_payload)
    mock_cattle_repository.get_cattle_by_id_and_company_id.assert_called_once_with(1, 1)


@pytest.mark.unit
def test_create_telemetry_step_raises_when_cattle_not_in_company(
    telemetry_create_payload, mocker
):
    mock_cattle_repository = mocker.Mock()
    mock_cattle_repository.get_cattle_by_id_and_company_id.return_value = None

    use_case = CreateTelemetryUseCase(
        repository=mocker.Mock(),
        cattle_repository=mock_cattle_repository,
        payload=telemetry_create_payload,
    )

    with pytest.raises(StopUseCaseException, match="Cattle not found"):
        CreateTelemetryStep(use_case=use_case).run()
