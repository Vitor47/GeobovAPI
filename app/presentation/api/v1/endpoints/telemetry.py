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
from app.presentation.api.v1.schemas.common import ErrorResponse
from app.presentation.api.v1.schemas.telemetry import (
    TelemetryCreate,
    TelemetryResponse,
)

router = APIRouter(tags=["Telemetry"])


@cbv(router)
class TelemetryController:
    @inject
    def __init__(
        self,
        create_telemetry_use_case_factory=Depends(
            Provide[Container.create_telemetry_use_case.provider]
        ),
        list_telemetry_use_case_factory=Depends(
            Provide[Container.list_telemetry_use_case.provider]
        ),
        get_telemetry_use_case_factory=Depends(
            Provide[Container.get_telemetry_use_case.provider]
        ),
    ):
        self.create_telemetry_use_case_factory = create_telemetry_use_case_factory
        self.list_telemetry_use_case_factory = list_telemetry_use_case_factory
        self.get_telemetry_use_case_factory = get_telemetry_use_case_factory

    @router.post(
        "/",
        response_model=TelemetryResponse,
        summary="Create telemetry sample",
        description=(
            "Stores a GPS telemetry sample for a cattle. Prefer gateway ingest "
            "(`POST /api/v1/gateways/ingest`) for LoRa field devices. "
            "Requires `cattle:create`."
        ),
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def create_telemetry(
        self,
        data: TelemetryCreate,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanCreateCattleDep,
    ):
        payload = CattleDataCreateDTO(
            cattle_id=data.cattle_id,
            lat=data.lat,
            lon=data.lon,
            company_id=company_id,
        )
        use_case = self.create_telemetry_use_case_factory(payload=payload)

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/",
        response_model=list[TelemetryResponse],
        summary="List telemetry",
        description="Returns telemetry records for the resolved company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def list_telemetry(
        self,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadCattleDep,
    ):
        use_case = self.list_telemetry_use_case_factory(company_id=company_id)

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/{telemetry_id}",
        response_model=TelemetryResponse,
        summary="Get telemetry",
        description="Returns a single telemetry record scoped to the company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Record not found."},
        },
    )
    def get_telemetry(
        self,
        telemetry_id: str,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadCattleDep,
    ):
        use_case = self.get_telemetry_use_case_factory(
            telemetry_id=telemetry_id,
            company_id=company_id,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if not use_case.data:
            raise HTTPException(status_code=404, detail="Telemetry not found")

        return use_case.data
