from app.application.dtos.company_dto import CompanyResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class ListCompaniesStep(BaseUseCaseStep):
    def _run(self):
        companies = self.use_case.repository.get_all_companies()

        self.use_case.data = [
            CompanyResponseDTO(id=c.id, name=c.name) for c in companies
        ]
