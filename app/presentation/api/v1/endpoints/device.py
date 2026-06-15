from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi_utils.cbv import cbv

from app.adapters.container import Container
from app.application.dtos.device_dto import (
    DeviceCreateDTO,
    DeviceTelemetryIngestDTO,
)
from app.core.auth.deps import (
    CanCreateDeviceDep,
    CanReadDeviceDep,
    CompanyIdDep,
)
from app.core.cache_utils.user_cache import CachedUser
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.common import ErrorResponse
from app.presentation.api.v1.schemas.device import (
    DeviceCreate,
    DeviceResponse,
    DeviceTelemetryIngest,
    DeviceTelemetryResponse,
)

router = APIRouter(tags=["Devices"])


@cbv(router)
class DeviceController:
    @inject
    def __init__(
        self,
        create_device_use_case_factory=Depends(
            Provide[Container.create_device_use_case.provider]
        ),
        get_devices_use_case_factory=Depends(
            Provide[Container.get_devices_use_case.provider]
        ),
        get_device_use_case_factory=Depends(
            Provide[Container.get_device_use_case.provider]
        ),
        ingest_telemetry_use_case_factory=Depends(
            Provide[Container.ingest_telemetry_use_case.provider]
        ),
    ):
        self.create_device_use_case_factory = create_device_use_case_factory
        self.get_devices_use_case_factory = get_devices_use_case_factory
        self.get_device_use_case_factory = get_device_use_case_factory
        self.ingest_telemetry_use_case_factory = ingest_telemetry_use_case_factory

    @router.post(
        "/",
        response_model=DeviceResponse,
        summary="Register device",
        description=(
            "Links a LoRa GPS device to a cattle. Returns an `api_key` used "
            "for telemetry ingestion. Requires `device:create`."
        ),
        responses={
            400: {"model": ErrorResponse, "description": "Validation error."},
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def create_device(
        self,
        data: DeviceCreate,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanCreateDeviceDep,
    ):
        payload = DeviceCreateDTO(
            serial_number=data.serial_number,
            cattle_id=data.cattle_id,
            company_id=company_id,
            name=data.name,
            transmission_interval_minutes=data.transmission_interval_minutes,
        )

        use_case = self.create_device_use_case_factory(
            payload=payload,
        )

        try:
            use_case.run()
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/",
        response_model=list[DeviceResponse],
        summary="List devices",
        description="Returns all devices for the resolved company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def get_devices(
        self,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadDeviceDep,
    ):
        use_case = self.get_devices_use_case_factory(
            company_id=company_id,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/{device_id}",
        response_model=DeviceResponse,
        summary="Get device",
        description="Returns a device by ID scoped to the company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Device not found."},
        },
    )
    def get_device(
        self,
        device_id: int,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadDeviceDep,
    ):
        use_case = self.get_device_use_case_factory(
            device_id=device_id,
            company_id=company_id,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if not use_case.data:
            raise HTTPException(status_code=404, detail="Device not found")

        return use_case.data

    @router.post(
        "/ingest",
        response_model=DeviceTelemetryResponse,
        summary="Ingest telemetry",
        description=(
            "LoRa device endpoint. Creates cattle telemetry and updates "
            "`last_seen_at`. Authenticated via `X-Device-Api-Key` header."
        ),
        responses={
            401: {"model": ErrorResponse, "description": "Invalid device API key."},
        },
    )
    def ingest_telemetry(
        self,
        data: DeviceTelemetryIngest,
        x_device_api_key: Annotated[
            str,
            Header(
                alias="X-Device-Api-Key",
                description="Device API key from registration.",
            ),
        ],
    ):
        payload = DeviceTelemetryIngestDTO(
            lat=data.lat,
            lon=data.lon,
            movement=data.movement,
            temperature=data.temperature,
        )

        use_case = self.ingest_telemetry_use_case_factory(
            api_key=x_device_api_key,
            payload=payload,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=401, detail=str(error)) from error

        return use_case.data
