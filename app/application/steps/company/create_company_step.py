from app.application.dtos.company_dto import CompanyResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class CreateCompanyStep(BaseUseCaseStep):
    def _run(self):
        company = self.use_case.repository.create_company(self.use_case.payload)

        self.use_case.data = CompanyResponseDTO(id=company.id, name=company.name)
