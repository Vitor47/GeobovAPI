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

        device = (
            self.use_case.device_repository.get_active_device_by_serial_and_company(
                serial_number=self.use_case.payload.device_serial,
                company_id=gateway.company_id,
            )
        )
        if not device:
            raise StopUseCaseException(
                "Unknown or inactive device for this gateway's company"
            )

        cattle_payload = CattleDataCreateDTO(
            cattle_id=device.cattle_id,
            lat=self.use_case.payload.lat,
            lon=self.use_case.payload.lon,
            company_id=device.company_id,
        )

        cattle_data = self.use_case.cattle_data_repository.create_cattle_data(
            cattle_payload
        )
        self.use_case.device_repository.update_last_seen(device.id)
        self.use_case.gateway_repository.update_last_seen(gateway.id)

        self.use_case.data = GatewayTelemetryResponseDTO(
            gateway_id=gateway.id,
            device_id=device.id,
            cattle_id=device.cattle_id,
            cattle_data_id=cattle_data.id,
            lat=cattle_data.lat,
            lon=cattle_data.lon,
        )
