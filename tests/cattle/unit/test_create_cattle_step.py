from unittest.mock import Mock

import pytest

from app.application.dtos.cattle_data_dto import CattleDataCreateDTO
from app.application.steps.cattle.create_cattle_step import CreateCattleStep
from app.application.use_cases.cattle.create_cattle_use_case import (
    CreateCattleUseCase,
)


@pytest.fixture
def cattle_create_payload() -> CattleDataCreateDTO:
    return CattleDataCreateDTO(
        cattle_id=1,
        lat=-23.55,
        lon=-46.63,
        movement=0.5,
        temperature=38.5,
        company_id=1,
    )


@pytest.fixture
def mock_cattle_data_record():
    record = Mock()
    record.id = 1
    record.cattle_id = 1
    record.lat = -23.55
    record.lon = -46.63
    record.movement = 0.5
    record.temperature = 38.5
    return record


@pytest.mark.unit
def test_create_cattle_step_sets_response_dto_when_record_is_created(
    cattle_create_payload, mock_cattle_data_record, mocker
):
    mock_repository = mocker.Mock()
    mock_repository.create_cattle.return_value = mock_cattle_data_record

    use_case = CreateCattleUseCase(
        repository=mock_repository,
        payload=cattle_create_payload,
    )

    CreateCattleStep(use_case=use_case).run()

    assert use_case.data.id == 1
    assert use_case.data.cattle_id == 1
    assert use_case.data.lat == -23.55
    assert use_case.data.lon == -46.63
    assert use_case.data.movement == 0.5
    assert use_case.data.temperature == 38.5
    mock_repository.create_cattle.assert_called_once_with(cattle_create_payload)


@pytest.mark.unit
def test_create_cattle_use_case_runs_create_step_when_executed(
    cattle_create_payload, mock_cattle_data_record, mocker
):
    mock_repository = mocker.Mock()
    mock_repository.create_cattle.return_value = mock_cattle_data_record

    use_case = CreateCattleUseCase(
        repository=mock_repository,
        payload=cattle_create_payload,
    )

    use_case.run()

    assert use_case.data is not None
    assert use_case.data.id == mock_cattle_data_record.id
    mock_repository.create_cattle.assert_called_once()
