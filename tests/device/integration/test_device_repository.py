import pytest

from app.adapters.repositories.device_repository import DeviceRepository
from app.application.dtos.device_dto import DeviceCreateDTO


@pytest.mark.integration
def test_create_device_persists_record_when_cattle_belongs_to_company(
    db_session, seeded_company, seeded_cattle
):
    repository = DeviceRepository(db=db_session)
    payload = DeviceCreateDTO(
        serial_number="LORA-001",
        cattle_id=seeded_cattle.id,
        company_id=seeded_company.id,
        name="Collar A",
    )

    result = repository.create_device(payload)

    assert result.id is not None
    assert result.cattle_id == seeded_cattle.id
    assert result.company_id == seeded_company.id
    assert result.api_key is not None
    assert result.transmission_interval_minutes == 5


@pytest.mark.integration
def test_create_device_raises_when_cattle_already_has_device(
    db_session, seeded_company, seeded_cattle
):
    repository = DeviceRepository(db=db_session)
    payload = DeviceCreateDTO(
        serial_number="LORA-001",
        cattle_id=seeded_cattle.id,
        company_id=seeded_company.id,
    )
    repository.create_device(payload)

    with pytest.raises(ValueError, match="already has a device"):
        repository.create_device(
            DeviceCreateDTO(
                serial_number="LORA-002",
                cattle_id=seeded_cattle.id,
                company_id=seeded_company.id,
            )
        )


@pytest.mark.integration
def test_ingest_flow_updates_cattle_location_via_device_api_key(
    db_session, seeded_company, seeded_cattle
):
    from app.adapters.models.cattle import CattleData
    from app.adapters.repositories.cattle_repository import CattleRepository
    from app.application.dtos.cattle_data_dto import CattleDataCreateDTO

    device_repo = DeviceRepository(db=db_session)
    device = device_repo.create_device(
        DeviceCreateDTO(
            serial_number="LORA-INGEST",
            cattle_id=seeded_cattle.id,
            company_id=seeded_company.id,
        )
    )

    found = device_repo.get_device_by_api_key(device.api_key)
    assert found is not None

    cattle_repo = CattleRepository(db=db_session)
    cattle_repo.create_cattle(
        CattleDataCreateDTO(
            cattle_id=device.cattle_id,
            lat=-23.55,
            lon=-46.63,
            movement=0.5,
            temperature=38.5,
            company_id=device.company_id,
        )
    )
    device_repo.update_last_seen(device.id)

    records = (
        db_session.query(CattleData)
        .filter(CattleData.cattle_id == seeded_cattle.id)
        .all()
    )
    assert len(records) == 1
    assert records[0].lat == -23.55

    db_session.refresh(device)
    assert device.last_seen_at is not None
