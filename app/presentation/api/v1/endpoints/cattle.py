from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from app.adapters.container import Container
from app.application.dtos.cattle_dto import CattleCreateDTO, CattleUpdateDTO
from app.core.auth.deps import (
    CanCreateCattleDep,
    CanReadCattleDep,
    CanUpdateCattleDep,
    CompanyIdDep,
)
from app.core.cache_utils.user_cache import CachedUser
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.cattle import (
    CattleCreate,
    CattleResponse,
    CattleUpdate,
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
        list_cattles_use_case_factory=Depends(
            Provide[Container.list_cattles_use_case.provider]
        ),
        get_cattle_use_case_factory=Depends(
            Provide[Container.get_cattle_use_case.provider]
        ),
        update_cattle_use_case_factory=Depends(
            Provide[Container.update_cattle_use_case.provider]
        ),
    ):
        self.create_cattle_use_case_factory = create_cattle_use_case_factory
        self.list_cattles_use_case_factory = list_cattles_use_case_factory
        self.get_cattle_use_case_factory = get_cattle_use_case_factory
        self.update_cattle_use_case_factory = update_cattle_use_case_factory

    @router.post(
        "/",
        response_model=CattleResponse,
        summary="Register cattle",
        description=(
            "Creates a cattle animal for the company (admin/manager). "
            "Requires `cattle:create`. Superusers must send `X-Company-Id`."
        ),
        responses={
            400: {"model": ErrorResponse, "description": "Validation error."},
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def create_cattle(
        self,
        data: CattleCreate,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanCreateCattleDep,
    ):
        payload = CattleCreateDTO(
            tag=data.tag,
            name=data.name,
            description=data.description,
            birth_date=data.birth_date,
            weight=data.weight,
            breed=data.breed,
            gender=data.gender,
            color=data.color,
            notes=data.notes,
            company_id=company_id,
        )
        use_case = self.create_cattle_use_case_factory(payload=payload)

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/",
        response_model=list[CattleResponse],
        summary="List cattle",
        description="Returns all cattle animals for the resolved company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def list_cattles(
        self,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanReadCattleDep,
    ):
        use_case = self.list_cattles_use_case_factory(company_id=company_id)

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.get(
        "/{cattle_id}",
        response_model=CattleResponse,
        summary="Get cattle",
        description="Returns a cattle animal scoped to the company.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Cattle not found."},
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

        if not use_case.data:
            raise HTTPException(status_code=404, detail="Cattle not found")

        return use_case.data

    @router.patch(
        "/{cattle_id}",
        response_model=CattleResponse,
        summary="Update cattle",
        description=(
            "Updates cattle fields including farmer observations (`notes`). "
            "Requires `cattle:update`."
        ),
        responses={
            400: {"model": ErrorResponse, "description": "Validation error."},
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
            404: {"model": ErrorResponse, "description": "Cattle not found."},
        },
    )
    def update_cattle(
        self,
        cattle_id: int,
        data: CattleUpdate,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanUpdateCattleDep,
    ):
        payload = CattleUpdateDTO(
            tag=data.tag,
            name=data.name,
            description=data.description,
            birth_date=data.birth_date,
            weight=data.weight,
            breed=data.breed,
            gender=data.gender,
            color=data.color,
            notes=data.notes,
            is_active=data.is_active,
        )
        use_case = self.update_cattle_use_case_factory(
            cattle_id=cattle_id,
            company_id=company_id,
            payload=payload,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            detail = str(error)
            status = 404 if detail == "Cattle not found for this company" else 400
            raise HTTPException(status_code=status, detail=detail) from error

        return use_case.data
