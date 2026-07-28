from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi_utils.cbv import cbv

from app.adapters.container import Container
from app.application.dtos.gateway_dto import (
    GatewayCreateDTO,
    GatewayTelemetryIngestDTO,
)
from app.core.auth.deps import (
    CanCreateGatewayDep,
    CanReadGatewayDep,
    CompanyIdDep,
)
from app.core.cache_utils.user_cache import CachedUser
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.common import ErrorResponse
from app.presentation.api.v1.schemas.gateway import (
    GatewayCreate,
    GatewayResponse,
    GatewayTelemetryIngest,
    GatewayTelemetryResponse,
)

router = APIRouter(tags=["Gateways"])


@cbv(router)
class GatewayController:
    @inject
    def __init__(
        self,
        create_gateway_use_case_factory=Depends(
            Provide[Container.create_gateway_use_case.provider]
        ),
        get_gateways_use_case_factory=Depends(
            Provide[Container.get_gateways_use_case.provider]
        ),
        get_gateway_use_case_factory=Depends(
            Provide[Container.get_gateway_use_case.provider]
        ),
        ingest_gateway_telemetry_use_case_factory=Depends(
            Provide[Container.ingest_gateway_telemetry_use_case.provider]
        ),
    ):
        self.create_gateway_use_case_factory = create_gateway_use_case_factory
        self.get_gateways_use_case_factory = get_gateways_use_case_factory
        self.get_gateway_use_case_factory = get_gateway_use_case_factory
        self.ingest_gateway_telemetry_use_case_factory = (
            ingest_gateway_telemetry_use_case_factory
        )

    @router.post(
        "/",
        response_model=GatewayResponse,
        summary="Register gateway",
        description=(
            "Registers a LoRa receiver/gateway for the company. Returns an "
            "`api_key` used for telemetry ingestion. Requires `gateway:create`."
        ),
        responses={
            400: {"model": ErrorResponse, "description": "Validation error."},
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def create_gateway(
        self,
        data: GatewayCreate,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanCreateGatewayDep,
    ):
        payload = GatewayCreateDTO(
            serial_number=data.serial_number,
            company_id=company_id,
            name=data.name,
        )

        use_case = self.create_gateway_use_case_factory(payload=payload)

        try:
            use_case.run()
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/",
        response_model=list[GatewayResponse],
        summary="List gateways",
        description="Returns all gateways for the resolved company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def get_gateways(
        self,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadGatewayDep,
    ):
        use_case = self.get_gateways_use_case_factory(company_id=company_id)

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/{gateway_id}",
        response_model=GatewayResponse,
        summary="Get gateway",
        description="Returns a gateway by ID scoped to the company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Gateway not found."},
        },
    )
    def get_gateway(
        self,
        gateway_id: int,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadGatewayDep,
    ):
        use_case = self.get_gateway_use_case_factory(
            gateway_id=gateway_id,
            company_id=company_id,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if not use_case.data:
            raise HTTPException(status_code=404, detail="Gateway not found")

        return use_case.data

    @router.post(
        "/ingest",
        response_model=GatewayTelemetryResponse,
        summary="Ingest telemetry via gateway",
        description=(
            "LoRa gateway endpoint. Authenticates with `X-Gateway-Api-Key`, "
            "resolves the collar by `device_serial` within the gateway's "
            "company, and stores GPS telemetry."
        ),
        responses={
            401: {
                "model": ErrorResponse,
                "description": "Invalid gateway key or unknown device.",
            },
        },
    )
    def ingest_telemetry(
        self,
        data: GatewayTelemetryIngest,
        x_gateway_api_key: Annotated[
            str,
            Header(
                alias="X-Gateway-Api-Key",
                description="Gateway API key from registration.",
            ),
        ],
    ):
        payload = GatewayTelemetryIngestDTO(
            device_serial=data.device_serial,
            lat=data.lat,
            lon=data.lon,
        )

        use_case = self.ingest_gateway_telemetry_use_case_factory(
            api_key=x_gateway_api_key,
            payload=payload,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=401, detail=str(error)) from error

        return use_case.data
