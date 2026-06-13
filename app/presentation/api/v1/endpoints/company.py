from fastapi import APIRouter
from fastapi_utils.cbv import cbv

from app.adapters.container import container
from app.core.auth.deps import CanReadCompanyDep
from app.core.cache_utils.user_cache import CachedUser
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.common import ErrorResponse
from app.presentation.api.v1.schemas.company import CompanyResponse

router = APIRouter(tags=["Companies"])


@cbv(router)
class CompanyController:
    @router.get(
        "/{company_id}",
        response_model=CompanyResponse,
        summary="Get company",
        description="Returns company details. Requires `company:read`.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Company not found."},
        },
    )
    def get_company(
        self,
        company_id: int,
        _: CachedUser = CanReadCompanyDep,
    ):
        use_case = container.get_company_use_case(company_id=company_id)

        try:
            use_case.run()
        except StopUseCaseException as error:
            return f"An unexpected error occurred: {error}"

        return use_case.data
