import pytest

from app.adapters.models.cattle import CattleData
from app.adapters.repositories.cattle_repository import CattleRepository
from app.application.dtos.cattle_data_dto import CattleDataCreateDTO


@pytest.mark.integration
def test_create_cattle_persists_record_when_payload_is_valid(
    db_session, seeded_company, seeded_cattle
):
    repository = CattleRepository(db=db_session)
    payload = CattleDataCreateDTO(
        cattle_id=seeded_cattle.id,
        lat=-23.55,
        lon=-46.63,
        movement=0.5,
        temperature=38.5,
        company_id=seeded_company.id,
    )

    result = repository.create_cattle(payload)

    assert result.id is not None
    assert result.cattle_id == seeded_cattle.id
    assert result.company_id == seeded_company.id

    stored = db_session.query(CattleData).filter(CattleData.id == result.id).first()
    assert stored is not None
    assert stored.temperature == 38.5


@pytest.mark.integration
def test_get_cattle_by_id_and_company_id_returns_none_when_not_found(
    db_session, seeded_company
):
    repository = CattleRepository(db=db_session)

    result = repository.get_cattle_by_id_and_company_id(
        cattle_id=999,
        company_id=seeded_company.id,
    )

    assert result is None


@pytest.mark.integration
def test_get_cattles_by_company_id_returns_only_company_records(
    db_session, seeded_company, seeded_cattle
):
    repository = CattleRepository(db=db_session)
    repository.create_cattle(
        CattleDataCreateDTO(
            cattle_id=seeded_cattle.id,
            lat=-23.55,
            lon=-46.63,
            movement=0.5,
            temperature=38.5,
            company_id=seeded_company.id,
        )
    )

    results = repository.get_cattles_by_company_id(seeded_company.id)

    assert len(results) == 1
    assert results[0].company_id == seeded_company.id
