from app.application.steps.cattle.cattle_mapper import cattle_to_response_dto
from app.domain.steps.base_use_case_step import BaseUseCaseStep
from app.domain.use_cases.exceptions import StopUseCaseException


class CreateCattleStep(BaseUseCaseStep):
    def _run(self):
        try:
            cattle = self.use_case.repository.create_cattle(self.use_case.payload)
        except ValueError as error:
            raise StopUseCaseException(str(error)) from error

        self.use_case.data = cattle_to_response_dto(cattle)
