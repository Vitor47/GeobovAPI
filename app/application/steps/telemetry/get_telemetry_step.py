from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetTelemetryStep(BaseUseCaseStep):
    def _run(self):
        cattle_data = self.use_case.repository.get_cattle_data_by_id_and_company_id(
            self.use_case.telemetry_id,
            self.use_case.company_id,
        )

        if not cattle_data:
            return

        self.use_case.data = CattleDataResponseDTO(
            id=cattle_data.id,
            cattle_id=cattle_data.cattle_id,
            lat=cattle_data.lat,
            lon=cattle_data.lon,
            timestamp=cattle_data.timestamp,
        )
