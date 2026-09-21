from app.application.dtos.cattle_data_dto import CattleDataCreateDTO
from app.application.dtos.gateway_dto import GatewayTelemetryResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep
from app.domain.use_cases.exceptions import StopUseCaseException


class IngestGatewayTelemetryStep(BaseUseCaseStep):
    def _run(self):
        gateway = self.use_case.gateway_repository.get_gateway_by_api_key(
            self.use_case.api_key
        )
        if not gateway:
            raise StopUseCaseException("Invalid or inactive gateway")

        payload = self.use_case.payload
        cattle = self.use_case.cattle_repository.get_cattle_by_id_and_company_id(
            payload.cow_id,
            gateway.company_id,
        )
        if not cattle:
            raise StopUseCaseException("Unknown cattle for this gateway's company")

        cattle_payload = CattleDataCreateDTO(
            cattle_id=cattle.id,
            lat=payload.lat,
            lon=payload.lon,
            company_id=gateway.company_id,
            protocol_version=payload.protocol_version,
            sequence=payload.sequence,
            satellites=payload.satellites,
            hdop=payload.hdop,
            rssi=payload.rssi,
            snr=payload.snr,
        )

        cattle_data = self.use_case.cattle_data_repository.create_cattle_data(
            cattle_payload
        )

        device = (
            self.use_case.device_repository.get_active_device_by_cattle_and_company(
                cattle_id=cattle.id,
                company_id=gateway.company_id,
            )
        )
        if device:
            self.use_case.device_repository.update_last_seen(device.id)

        self.use_case.gateway_repository.update_last_seen(gateway.id)

        self.use_case.data = GatewayTelemetryResponseDTO(
            gateway_id=gateway.id,
            device_id=device.id if device else None,
            cattle_id=cattle.id,
            cattle_data_id=cattle_data.id,
            protocol_version=payload.protocol_version,
            lat=cattle_data.lat,
            lon=cattle_data.lon,
            sequence=payload.sequence,
            satellites=payload.satellites,
            hdop=payload.hdop,
            rssi=payload.rssi,
            snr=payload.snr,
        )
