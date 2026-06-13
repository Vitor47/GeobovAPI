from app.application.dtos.company_dto import CompanyResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetCompanyStep(BaseUseCaseStep):

    def _run(self):
        company = self.use_case.repository.get_company_by_id(self.use_case.company_id)

        if not company:
            return

        self.use_case.data = CompanyResponseDTO(id=company.id, name=company.name)
