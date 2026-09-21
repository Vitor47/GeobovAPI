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
    assert result.serial_number == "LORA-001"
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
def test_get_active_device_by_serial_and_company(
    db_session, seeded_company, seeded_cattle
):
    repository = DeviceRepository(db=db_session)
    repository.create_device(
        DeviceCreateDTO(
            serial_number="LORA-INGEST",
            cattle_id=seeded_cattle.id,
            company_id=seeded_company.id,
        )
    )

    found = repository.get_active_device_by_serial_and_company(
        "LORA-INGEST",
        seeded_company.id,
    )
    assert found is not None
    assert found.serial_number == "LORA-INGEST"

    missing = repository.get_active_device_by_serial_and_company(
        "LORA-INGEST",
        company_id=999,
    )
    assert missing is None


@pytest.mark.integration
def test_get_active_device_by_cattle_and_company(
    db_session, seeded_company, seeded_cattle
):
    repository = DeviceRepository(db=db_session)
    repository.create_device(
        DeviceCreateDTO(
            serial_number="LORA-COW",
            cattle_id=seeded_cattle.id,
            company_id=seeded_company.id,
        )
    )

    found = repository.get_active_device_by_cattle_and_company(
        cattle_id=seeded_cattle.id,
        company_id=seeded_company.id,
    )
    assert found is not None
    assert found.cattle_id == seeded_cattle.id

    missing = repository.get_active_device_by_cattle_and_company(
        cattle_id=seeded_cattle.id,
        company_id=999,
    )
    assert missing is None
