import pytest
from bson import ObjectId

from app.adapters.models import Company
from app.adapters.repositories.cattle_data_repository import CattleDataRepository
from app.adapters.repositories.cattle_repository import CattleRepository
from app.adapters.repositories.device_repository import DeviceRepository
from app.adapters.repositories.gateway_repository import GatewayRepository
from app.application.dtos.device_dto import DeviceCreateDTO
from app.application.dtos.gateway_dto import (
    GatewayCreateDTO,
    GatewayTelemetryIngestDTO,
)
from app.application.steps.gateway.ingest_gateway_telemetry_step import (
    IngestGatewayTelemetryStep,
)
from app.application.use_cases.gateway.ingest_gateway_telemetry_use_case import (
    IngestGatewayTelemetryUseCase,
)
from app.domain.use_cases.exceptions import StopUseCaseException


@pytest.mark.integration
def test_create_gateway_persists_api_key(db_session, seeded_company):
    repository = GatewayRepository(db=db_session)
    result = repository.create_gateway(
        GatewayCreateDTO(
            serial_number="GW-001",
            company_id=seeded_company.id,
            name="Barn",
        )
    )

    assert result.id is not None
    assert result.api_key is not None
    assert result.company_id == seeded_company.id


@pytest.mark.integration
def test_gateway_ingest_flow_associates_telemetry_by_cow_id(
    db_session, seeded_company, seeded_cattle, mongo_db
):
    gateway_repo = GatewayRepository(db=db_session)
    cattle_repo = CattleRepository(db=db_session)
    device_repo = DeviceRepository(db=db_session)
    cattle_data_repo = CattleDataRepository(db=mongo_db)

    gateway = gateway_repo.create_gateway(
        GatewayCreateDTO(
            serial_number="GW-INGEST",
            company_id=seeded_company.id,
        )
    )
    device = device_repo.create_device(
        DeviceCreateDTO(
            serial_number="LORA-COLLAR-001",
            cattle_id=seeded_cattle.id,
            company_id=seeded_company.id,
        )
    )

    use_case = IngestGatewayTelemetryUseCase(
        gateway_repository=gateway_repo,
        cattle_repository=cattle_repo,
        device_repository=device_repo,
        cattle_data_repository=cattle_data_repo,
        api_key=gateway.api_key,
        payload=GatewayTelemetryIngestDTO(
            protocol_version=1,
            cow_id=seeded_cattle.id,
            lat=-29.6732,
            lon=-53.8113,
            sequence=27,
            satellites=9,
            hdop=1.2,
            rssi=-83,
            snr=6.75,
        ),
    )
    IngestGatewayTelemetryStep(use_case=use_case).run()

    assert use_case.data is not None
    assert use_case.data.device_id == device.id
    assert use_case.data.gateway_id == gateway.id
    assert use_case.data.cattle_id == seeded_cattle.id
    assert use_case.data.sequence == 27

    records = cattle_data_repo.get_cattle_data_by_company_id(seeded_company.id)
    assert len(records) == 1
    assert records[0].cattle_id == seeded_cattle.id
    assert records[0].sequence == 27
    assert records[0].satellites == 9
    assert records[0].hdop == 1.2
    assert records[0].rssi == -83
    assert records[0].snr == 6.75

    stored = mongo_db["cattle_telemetry"].find_one({"_id": ObjectId(records[0].id)})
    assert stored["protocol_version"] == 1
    assert stored["sequence"] == 27

    db_session.refresh(device)
    db_session.refresh(gateway)
    assert device.last_seen_at is not None
    assert gateway.last_seen_at is not None


@pytest.mark.integration
def test_gateway_ingest_rejects_cow_id_from_another_company(
    db_session, seeded_company, seeded_cattle, mongo_db
):
    gateway_repo = GatewayRepository(db=db_session)
    cattle_repo = CattleRepository(db=db_session)
    device_repo = DeviceRepository(db=db_session)
    cattle_data_repo = CattleDataRepository(db=mongo_db)

    other_company = Company(name="Other Farm")
    db_session.add(other_company)
    db_session.commit()
    db_session.refresh(other_company)

    gateway = gateway_repo.create_gateway(
        GatewayCreateDTO(
            serial_number="GW-OTHER",
            company_id=other_company.id,
        )
    )

    use_case = IngestGatewayTelemetryUseCase(
        gateway_repository=gateway_repo,
        cattle_repository=cattle_repo,
        device_repository=device_repo,
        cattle_data_repository=cattle_data_repo,
        api_key=gateway.api_key,
        payload=GatewayTelemetryIngestDTO(
            protocol_version=1,
            cow_id=seeded_cattle.id,
            lat=-29.6732,
            lon=-53.8113,
            sequence=1,
            satellites=8,
            hdop=1.0,
            rssi=-80,
            snr=5.0,
        ),
    )

    with pytest.raises(StopUseCaseException, match="Unknown cattle"):
        IngestGatewayTelemetryStep(use_case=use_case).run()
