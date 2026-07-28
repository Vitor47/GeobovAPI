from unittest.mock import Mock

import pytest

from app.application.dtos.cattle_dto import CattleCreateDTO
from app.application.steps.cattle.create_cattle_step import CreateCattleStep
from app.application.use_cases.cattle.create_cattle_use_case import (
    CreateCattleUseCase,
)
from app.domain.use_cases.exceptions import StopUseCaseException


@pytest.fixture
def cattle_create_payload() -> CattleCreateDTO:
    return CattleCreateDTO(
        tag="BR-001",
        name="Mimosa",
        company_id=1,
        notes="Initial note",
    )


@pytest.fixture
def mock_cattle_record():
    record = Mock()
    record.id = 1
    record.tag = "BR-001"
    record.name = "Mimosa"
    record.company_id = 1
    record.is_active = True
    record.description = None
    record.birth_date = None
    record.weight = None
    record.breed = None
    record.gender = None
    record.color = None
    record.notes = "Initial note"
    return record


@pytest.mark.unit
def test_create_cattle_step_sets_response_dto_when_animal_is_created(
    cattle_create_payload, mock_cattle_record, mocker
):
    mock_repository = mocker.Mock()
    mock_repository.create_cattle.return_value = mock_cattle_record

    use_case = CreateCattleUseCase(
        repository=mock_repository,
        payload=cattle_create_payload,
    )

    CreateCattleStep(use_case=use_case).run()

    assert use_case.data.id == 1
    assert use_case.data.tag == "BR-001"
    assert use_case.data.name == "Mimosa"
    assert use_case.data.notes == "Initial note"
    mock_repository.create_cattle.assert_called_once_with(cattle_create_payload)


@pytest.mark.unit
def test_create_cattle_step_raises_when_tag_already_exists(
    cattle_create_payload, mocker
):
    mock_repository = mocker.Mock()
    mock_repository.create_cattle.side_effect = ValueError(
        "Cattle tag already exists for this company"
    )

    use_case = CreateCattleUseCase(
        repository=mock_repository,
        payload=cattle_create_payload,
    )

    with pytest.raises(StopUseCaseException, match="already exists"):
        CreateCattleStep(use_case=use_case).run()
