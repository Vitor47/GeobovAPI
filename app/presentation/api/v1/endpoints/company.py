from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from app.adapters.container import Container
from app.core.auth.deps import CanReadCompanyDep, CompanyIdDep
from app.core.cache_utils.user_cache import CachedUser
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.common import ErrorResponse
from app.presentation.api.v1.schemas.company import CompanyResponse

router = APIRouter(tags=["Companies"])


@cbv(router)
class CompanyController:
    @inject
    def __init__(
        self,
        get_company_use_case_factory=Depends(
            Provide[Container.get_company_use_case.provider]
        ),
    ):
        self.get_company_use_case_factory = get_company_use_case_factory

    @router.get(
        "/me",
        response_model=CompanyResponse,
        summary="Get current company",
        description=(
            "Returns the company scoped to the authenticated user "
            "(or `X-Company-Id` for superusers). Requires `company:read`."
        ),
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Company not found."},
        },
    )
    def get_my_company(
        self,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadCompanyDep,
    ):
        use_case = self.get_company_use_case_factory(
            company_id=company_id,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if not use_case.data:
            raise HTTPException(status_code=404, detail="Company not found")

        return use_case.data
