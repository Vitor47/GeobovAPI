from app.application.dtos.device_dto import DeviceResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetDeviceStep(BaseUseCaseStep):
    def _run(self):
        device = self.use_case.repository.get_device_by_id_and_company_id(
            self.use_case.device_id, self.use_case.company_id
        )

        if not device:
            return

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
