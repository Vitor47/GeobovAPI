from app.application.steps.cattle.cattle_mapper import cattle_to_response_dto
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class ListCattlesStep(BaseUseCaseStep):
    def _run(self):
        cattles = self.use_case.repository.get_cattles_by_company_id(
            self.use_case.company_id
        )
        self.use_case.data = [cattle_to_response_dto(cattle) for cattle in cattles]
