from app.application.dtos.company_dto import CompanyListResultDTO, CompanyResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class ListCompaniesStep(BaseUseCaseStep):
    def _run(self):
        page = max(int(getattr(self.use_case, "page", 1) or 1), 1)
        page_size = min(max(int(getattr(self.use_case, "page_size", 20) or 20), 1), 100)
        query = getattr(self.use_case, "query", None)
        company_ids = getattr(self.use_case, "company_ids", None)

        companies, total = self.use_case.repository.search_companies(
            company_ids=company_ids,
            query=query,
            page=page,
            page_size=page_size,
        )

        items = [CompanyResponseDTO(id=c.id, name=c.name) for c in companies]
        self.use_case.data = CompanyListResultDTO(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total,
        )
