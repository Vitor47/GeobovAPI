import pytest

from app.adapters.repositories.cattle_repository import CattleRepository
from app.application.dtos.cattle_dto import CattleCreateDTO, CattleUpdateDTO


@pytest.mark.integration
def test_create_cattle_persists_animal_when_payload_is_valid(
    db_session, seeded_company
):
    repository = CattleRepository(db=db_session)
    payload = CattleCreateDTO(
        tag="BR-001",
        name="Mimosa",
        company_id=seeded_company.id,
        notes="Auction 2026",
    )

    result = repository.create_cattle(payload)

    assert result.id is not None
    assert result.tag == "BR-001"
    assert result.company_id == seeded_company.id
    assert result.notes == "Auction 2026"


@pytest.mark.integration
def test_create_cattle_raises_when_tag_already_exists(db_session, seeded_company):
    repository = CattleRepository(db=db_session)
    payload = CattleCreateDTO(
        tag="BR-001",
        name="Mimosa",
        company_id=seeded_company.id,
    )
    repository.create_cattle(payload)

    with pytest.raises(ValueError, match="already exists"):
        repository.create_cattle(
            CattleCreateDTO(
                tag="BR-001",
                name="Other",
                company_id=seeded_company.id,
            )
        )


@pytest.mark.integration
def test_update_cattle_updates_notes_when_animal_exists(
    db_session, seeded_company, seeded_cattle
):
    repository = CattleRepository(db=db_session)

    updated = repository.update_cattle(
        cattle_id=seeded_cattle.id,
        company_id=seeded_company.id,
        data=CattleUpdateDTO(notes="Observed near north fence"),
    )

    assert updated.notes == "Observed near north fence"


@pytest.mark.integration
def test_get_cattles_by_company_id_returns_only_company_animals(
    db_session, seeded_company, seeded_cattle
):
    repository = CattleRepository(db=db_session)

    results = repository.get_cattles_by_company_id(seeded_company.id)

    assert len(results) == 1
    assert results[0].id == seeded_cattle.id
