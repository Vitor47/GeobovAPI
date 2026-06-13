from fastapi import APIRouter
from fastapi_utils.cbv import cbv

from app.adapters.container import container
from app.application.dtos.cattle_data_dto import CattleDataCreateDTO
from app.core.auth.deps import (
    CanCreateCattleDep,
    CanReadCattleDep,
    CompanyIdDep,
)
from app.core.cache_utils.user_cache import CachedUser
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.cattle import (
    CattleDataCreate,
    CattleDataResponse,
)
from app.presentation.api.v1.schemas.common import ErrorResponse

router = APIRouter(tags=["Cattle"])


@cbv(router)
class CattleController:
    @router.post(
        "/",
        response_model=CattleDataResponse,
        summary="Create cattle telemetry",
        description=(
            "Stores a telemetry snapshot for a cattle. Requires `cattle:create`. "
            "Superusers must send `X-Company-Id`."
        ),
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def create_cattle(
        self,
        data: CattleDataCreate,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanCreateCattleDep,
    ):
        payload = CattleDataCreateDTO(
            cattle_id=data.cattle_id,
            lat=data.lat,
            lon=data.lon,
            movement=data.movement,
            temperature=data.temperature,
            company_id=company_id,
        )

        use_case = container.create_cattle_use_case(payload=payload)

        try:
            use_case.run()
        except StopUseCaseException as error:
            return f"An unexpected error occurred: {error}"

        return use_case.data

    @router.get(
        "/",
        response_model=list[CattleDataResponse],
        summary="List cattle telemetry",
        description="Returns all telemetry records for the resolved company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def get_cattles(
        self,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadCattleDep,
    ):
        use_case = container.get_cattles_use_case(company_id=company_id)

        try:
            use_case.run()
        except StopUseCaseException as error:
            return f"An unexpected error occurred: {error}"

        return use_case.data

    @router.get(
        "/{cattle_id}",
        response_model=CattleDataResponse,
        summary="Get cattle telemetry",
        description="Returns a single telemetry record scoped to the company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Record not found."},
        },
    )
    def get_cattle(
        self,
        cattle_id: int,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadCattleDep,
    ):
        use_case = container.get_cattle_use_case(
            cattle_id=cattle_id, company_id=company_id
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            return f"An unexpected error occurred: {error}"

        return use_case.data
