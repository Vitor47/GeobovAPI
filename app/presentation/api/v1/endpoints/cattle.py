from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from app.adapters.container import Container
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
    @inject
    def __init__(
        self,
        create_cattle_use_case_factory=Depends(
            Provide[Container.create_cattle_use_case.provider]
        ),
        get_cattles_use_case_factory=Depends(
            Provide[Container.get_cattles_use_case.provider]
        ),
        get_cattle_use_case_factory=Depends(
            Provide[Container.get_cattle_use_case.provider]
        ),
    ):
        self.create_cattle_use_case_factory = create_cattle_use_case_factory
        self.get_cattles_use_case_factory = get_cattles_use_case_factory
        self.get_cattle_use_case_factory = get_cattle_use_case_factory

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
    def create_cattle_telemetry(
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

        use_case = self.create_cattle_use_case_factory(
            payload=payload,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

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
        use_case = self.get_cattles_use_case_factory(
            company_id=company_id,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

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
        use_case = self.get_cattle_use_case_factory(
            cattle_id=cattle_id,
            company_id=company_id,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data
