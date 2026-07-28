from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class ListTelemetryStep(BaseUseCaseStep):
    def _run(self):
        records = self.use_case.repository.get_cattle_data_by_company_id(
            self.use_case.company_id
        )

        self.use_case.data = [
            CattleDataResponseDTO(
                id=record.id,
                cattle_id=record.cattle_id,
                lat=record.lat,
                lon=record.lon,
                timestamp=record.timestamp,
            )
            for record in records
        ]
