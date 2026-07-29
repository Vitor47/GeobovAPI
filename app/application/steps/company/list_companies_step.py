from app.application.dtos.company_dto import CompanyResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class ListCompaniesStep(BaseUseCaseStep):
    def _run(self):
        company_ids = getattr(self.use_case, "company_ids", None)

        if company_ids is None:
            companies = self.use_case.repository.get_all_companies()
        else:
            companies = self.use_case.repository.get_companies_by_ids(company_ids)

        self.use_case.data = [
            CompanyResponseDTO(id=c.id, name=c.name) for c in companies
        ]
