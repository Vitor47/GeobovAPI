from app.application.steps.cattle.cattle_mapper import cattle_to_response_dto
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetCattleStep(BaseUseCaseStep):
    def _run(self):
        cattle = self.use_case.repository.get_cattle_by_id_and_company_id(
            self.use_case.cattle_id,
            self.use_case.company_id,
        )
        if not cattle:
            return

        self.use_case.data = cattle_to_response_dto(cattle)
