from app.application.dtos.cattle_data_dto import CattleDataCreateDTO
from app.application.dtos.device_dto import DeviceTelemetryResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep
from app.domain.use_cases.exceptions import StopUseCaseException


class IngestTelemetryStep(BaseUseCaseStep):
    def _run(self):
        device = self.use_case.device_repository.get_device_by_api_key(
            self.use_case.api_key
        )

        if not device:
            raise StopUseCaseException("Invalid or inactive device")

        cattle_payload = CattleDataCreateDTO(
            cattle_id=device.cattle_id,
            lat=self.use_case.payload.lat,
            lon=self.use_case.payload.lon,
            movement=self.use_case.payload.movement,
            temperature=self.use_case.payload.temperature,
            company_id=device.company_id,
        )

        cattle_data = self.use_case.cattle_repository.create_cattle(cattle_payload)
        self.use_case.device_repository.update_last_seen(device.id)

        self.use_case.data = DeviceTelemetryResponseDTO(
            device_id=device.id,
            cattle_id=device.cattle_id,
            cattle_data_id=cattle_data.id,
            lat=cattle_data.lat,
            lon=cattle_data.lon,
            movement=cattle_data.movement,
            temperature=cattle_data.temperature,
        )
