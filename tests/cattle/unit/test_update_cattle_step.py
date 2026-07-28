from unittest.mock import Mock

import pytest

from app.application.dtos.cattle_dto import CattleUpdateDTO
from app.application.steps.cattle.update_cattle_step import UpdateCattleStep
from app.application.use_cases.cattle.update_cattle_use_case import (
    UpdateCattleUseCase,
)


@pytest.mark.unit
def test_update_cattle_step_sets_notes_when_observation_is_saved(mocker):
    mock_cattle = Mock()
    mock_cattle.id = 1
    mock_cattle.tag = "BR-001"
    mock_cattle.name = "Mimosa"
    mock_cattle.company_id = 1
    mock_cattle.is_active = True
    mock_cattle.description = None
    mock_cattle.birth_date = None
    mock_cattle.weight = None
    mock_cattle.breed = None
    mock_cattle.gender = None
    mock_cattle.color = None
    mock_cattle.notes = "Limping"

    mock_repository = mocker.Mock()
    mock_repository.update_cattle.return_value = mock_cattle

    payload = CattleUpdateDTO(notes="Limping")
    use_case = UpdateCattleUseCase(
        repository=mock_repository,
        cattle_id=1,
        company_id=1,
        payload=payload,
    )

    UpdateCattleStep(use_case=use_case).run()

    assert use_case.data.notes == "Limping"
    mock_repository.update_cattle.assert_called_once_with(
        cattle_id=1,
        company_id=1,
        data=payload,
    )
