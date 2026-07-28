import pytest

from app.adapters.repositories.cattle_data_repository import CattleDataRepository
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
def test_gateway_ingest_flow_scopes_device_to_gateway_company(
    db_session, seeded_company, seeded_cattle, mongo_db
):
    gateway_repo = GatewayRepository(db=db_session)
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
        device_repository=device_repo,
        cattle_data_repository=cattle_data_repo,
        api_key=gateway.api_key,
        payload=GatewayTelemetryIngestDTO(
            device_serial=device.serial_number,
            lat=-23.55,
            lon=-46.63,
        ),
    )
    IngestGatewayTelemetryStep(use_case=use_case).run()

    assert use_case.data is not None
    assert use_case.data.device_id == device.id
    assert use_case.data.gateway_id == gateway.id

    records = cattle_data_repo.get_cattle_data_by_company_id(seeded_company.id)
    assert len(records) == 1

    db_session.refresh(device)
    db_session.refresh(gateway)
    assert device.last_seen_at is not None
    assert gateway.last_seen_at is not None
