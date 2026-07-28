from app.application.dtos.device_dto import DeviceResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetDevicesStep(BaseUseCaseStep):
    def _run(self):
        devices = self.use_case.repository.get_devices_by_company_id(
            self.use_case.company_id
        )

        self.use_case.data = [
            DeviceResponseDTO(
                id=d.id,
                serial_number=d.serial_number,
                name=d.name,
                cattle_id=d.cattle_id,
                company_id=d.company_id,
                is_active=d.is_active,
                transmission_interval_minutes=d.transmission_interval_minutes,
                last_seen_at=d.last_seen_at,
            )
            for d in devices
        ]
