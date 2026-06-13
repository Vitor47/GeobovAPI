from app.application.dtos.device_dto import DeviceResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class CreateDeviceStep(BaseUseCaseStep):
    def _run(self):
        device = self.use_case.repository.create_device(self.use_case.payload)

        self.use_case.data = DeviceResponseDTO(
            id=device.id,
            serial_number=device.serial_number,
            name=device.name,
            cattle_id=device.cattle_id,
            company_id=device.company_id,
            api_key=device.api_key,
            is_active=device.is_active,
            transmission_interval_minutes=device.transmission_interval_minutes,
            last_seen_at=device.last_seen_at,
        )
