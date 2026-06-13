from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetCattlesStep(BaseUseCaseStep):
    def _run(self):
        cattles = self.use_case.repository.get_cattles_by_company_id(
            self.use_case.company_id
        )

        self.use_case.data = [
            CattleDataResponseDTO(
                id=c.id,
                cattle_id=c.cattle_id,
                lat=c.lat,
                lon=c.lon,
                movement=c.movement,
                temperature=c.temperature,
            )
            for c in cattles
        ]
