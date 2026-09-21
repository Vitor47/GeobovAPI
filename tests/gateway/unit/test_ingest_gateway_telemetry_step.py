from unittest.mock import Mock

import pytest

from app.application.dtos.gateway_dto import GatewayTelemetryIngestDTO
from app.application.steps.gateway.ingest_gateway_telemetry_step import (
    IngestGatewayTelemetryStep,
)
from app.application.use_cases.gateway.ingest_gateway_telemetry_use_case import (
    IngestGatewayTelemetryUseCase,
)
from app.domain.use_cases.exceptions import StopUseCaseException


@pytest.fixture
def ingest_payload() -> GatewayTelemetryIngestDTO:
    return GatewayTelemetryIngestDTO(
        protocol_version=1,
        cow_id=10,
        lat=-29.6732,
        lon=-53.8113,
        sequence=27,
        satellites=9,
        hdop=1.2,
        rssi=-83,
        snr=6.75,
    )


def _build_use_case(
    mocker,
    ingest_payload,
    *,
    gateway=None,
    cattle=None,
    device=None,
    cattle_data=None,
    api_key: str = "gateway-key",
):
    mock_gateway_repo = mocker.Mock()
    mock_gateway_repo.get_gateway_by_api_key.return_value = gateway

    mock_cattle_repo = mocker.Mock()
    mock_cattle_repo.get_cattle_by_id_and_company_id.return_value = cattle

    mock_device_repo = mocker.Mock()
    mock_device_repo.get_active_device_by_cattle_and_company.return_value = device

    mock_cattle_data_repo = mocker.Mock()
    mock_cattle_data_repo.create_cattle_data.return_value = cattle_data

    return IngestGatewayTelemetryUseCase(
        gateway_repository=mock_gateway_repo,
        cattle_repository=mock_cattle_repo,
        device_repository=mock_device_repo,
        cattle_data_repository=mock_cattle_data_repo,
        api_key=api_key,
        payload=ingest_payload,
    )


@pytest.mark.unit
def test_ingest_gateway_telemetry_resolves_cattle_by_cow_id_and_creates_data(
    ingest_payload, mocker
):
    mock_gateway = Mock()
    mock_gateway.id = 5
    mock_gateway.company_id = 1

    mock_cattle = Mock()
    mock_cattle.id = 10

    mock_device = Mock()
    mock_device.id = 1

    mock_cattle_data = Mock()
    mock_cattle_data.id = "507f1f77bcf86cd799439011"
    mock_cattle_data.lat = -29.6732
    mock_cattle_data.lon = -53.8113

    use_case = _build_use_case(
        mocker,
        ingest_payload,
        gateway=mock_gateway,
        cattle=mock_cattle,
        device=mock_device,
        cattle_data=mock_cattle_data,
    )

    IngestGatewayTelemetryStep(use_case=use_case).run()

    cattle_lookup = use_case.cattle_repository.get_cattle_by_id_and_company_id
    device_lookup = use_case.device_repository.get_active_device_by_cattle_and_company

    assert use_case.data.gateway_id == 5
    assert use_case.data.device_id == 1
    assert use_case.data.cattle_id == 10
    assert use_case.data.cattle_data_id == "507f1f77bcf86cd799439011"
    assert use_case.data.sequence == 27
    assert use_case.data.satellites == 9
    assert use_case.data.hdop == 1.2
    assert use_case.data.rssi == -83
    assert use_case.data.snr == 6.75
    cattle_lookup.assert_called_once_with(10, 1)
    device_lookup.assert_called_once_with(cattle_id=10, company_id=1)
    use_case.device_repository.update_last_seen.assert_called_once_with(1)
    use_case.gateway_repository.update_last_seen.assert_called_once_with(5)


@pytest.mark.unit
def test_ingest_succeeds_without_linked_device(ingest_payload, mocker):
    mock_gateway = Mock()
    mock_gateway.id = 5
    mock_gateway.company_id = 1

    mock_cattle = Mock()
    mock_cattle.id = 10

    mock_cattle_data = Mock()
    mock_cattle_data.id = "507f1f77bcf86cd799439011"
    mock_cattle_data.lat = -29.6732
    mock_cattle_data.lon = -53.8113

    use_case = _build_use_case(
        mocker,
        ingest_payload,
        gateway=mock_gateway,
        cattle=mock_cattle,
        device=None,
        cattle_data=mock_cattle_data,
    )

    IngestGatewayTelemetryStep(use_case=use_case).run()

    assert use_case.data.device_id is None
    use_case.device_repository.update_last_seen.assert_not_called()
    use_case.gateway_repository.update_last_seen.assert_called_once_with(5)


@pytest.mark.unit
def test_ingest_raises_when_gateway_api_key_is_invalid(ingest_payload, mocker):
    use_case = _build_use_case(
        mocker,
        ingest_payload,
        gateway=None,
        api_key="bad-key",
    )

    with pytest.raises(StopUseCaseException, match="Invalid or inactive gateway"):
        IngestGatewayTelemetryStep(use_case=use_case).run()


@pytest.mark.unit
def test_ingest_raises_when_cow_id_is_unknown(ingest_payload, mocker):
    mock_gateway = Mock()
    mock_gateway.id = 5
    mock_gateway.company_id = 1

    use_case = _build_use_case(
        mocker,
        ingest_payload,
        gateway=mock_gateway,
        cattle=None,
    )

    with pytest.raises(StopUseCaseException, match="Unknown cattle"):
        IngestGatewayTelemetryStep(use_case=use_case).run()
