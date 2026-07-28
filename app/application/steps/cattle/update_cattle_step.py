from app.application.steps.cattle.cattle_mapper import cattle_to_response_dto
from app.domain.steps.base_use_case_step import BaseUseCaseStep
from app.domain.use_cases.exceptions import StopUseCaseException


class UpdateCattleStep(BaseUseCaseStep):
    def _run(self):
        try:
            cattle = self.use_case.repository.update_cattle(
                cattle_id=self.use_case.cattle_id,
                company_id=self.use_case.company_id,
                data=self.use_case.payload,
            )
        except ValueError as error:
            raise StopUseCaseException(str(error)) from error

        self.use_case.data = cattle_to_response_dto(cattle)
