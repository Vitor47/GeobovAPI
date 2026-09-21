from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class ListTelemetryStep(BaseUseCaseStep):
    def _run(self):
        records = self.use_case.repository.get_cattle_data_by_company_id(
            self.use_case.company_id
        )

        self.use_case.data = [
            CattleDataResponseDTO.from_entity(record) for record in records
        ]
