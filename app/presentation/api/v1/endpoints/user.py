from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from app.adapters.container import Container
from app.application.dtos.user_dto import UserLoginDTO
from app.core.auth.deps import CanCreateUserDep, CompanyIdDep, CurrentUserDep
from app.core.cache_utils.user_cache import (
    CachedUser,
    cache_user_from_payload,
    invalidate_user_session,
)
from app.core.security import create_access_token
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.common import ErrorResponse, MessageResponse
from app.presentation.api.v1.schemas.user import (
    SwitchCompanyRequest,
    UserCreate,
    UserLogin,
    UserLoginResponse,
    UserResponse,
)

router = APIRouter(tags=["Users"])


@cbv(router)
class UserController:
    @inject
    def __init__(
        self,
        authenticate_user_use_case_factory=Depends(
            Provide[Container.authenticate_user_use_case.provider]
        ),
        create_user_use_case_factory=Depends(
            Provide[Container.create_user_use_case.provider]
        ),
        get_company_use_case_factory=Depends(
            Provide[Container.get_company_use_case.provider]
        ),
    ):
        self.authenticate_user_use_case_factory = authenticate_user_use_case_factory
        self.create_user_use_case_factory = create_user_use_case_factory
        self.get_company_use_case_factory = get_company_use_case_factory

    @router.post(
        "/",
        response_model=UserResponse,
        summary="Create user",
        description=(
            "Creates a user in the authenticated user's company. "
            "Requires the `user:create` permission."
        ),
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Missing permission."},
        },
    )
    def create_user(
        self,
        data: UserCreate,
        company_id: int = CompanyIdDep,
        _: CachedUser = CanCreateUserDep,
    ):
        data.company_id = company_id

        use_case = self.create_user_use_case_factory(
            payload=data,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return use_case.data

    @router.post(
        "/login",
        response_model=UserLoginResponse,
        summary="Login",
        description=(
            "Authenticates with email and password. Returns a JWT scoped to the "
            "user's default/active farm (`company_id`)."
        ),
        responses={
            401: {"model": ErrorResponse, "description": "Invalid credentials."},
        },
    )
    def login(
        self,
        data: UserLogin,
    ):
        payload = UserLoginDTO(email=data.email, password=data.password)

        use_case = self.authenticate_user_use_case_factory(
            email=payload.email,
            password=payload.password,
        )

        try:
            use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if not use_case.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return use_case.data

    @router.post(
        "/switch-company",
        response_model=UserLoginResponse,
        summary="Switch active farm",
        description=(
            "Issues a new JWT with `company_id` set to the selected farm. "
            "Farmers may only switch to memberships; "
            "superusers may switch to any farm. "
            "Clients should stop sending X-Company-Id and rely on the token."
        ),
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
            403: {"model": ErrorResponse, "description": "Farm not allowed."},
            404: {"model": ErrorResponse, "description": "Farm not found."},
        },
    )
    def switch_company(
        self,
        data: SwitchCompanyRequest,
        current_user: CachedUser = CurrentUserDep,
    ):
        membership_ids = list(current_user.company_ids or [])
        if not current_user.is_superuser and data.company_id not in membership_ids:
            raise HTTPException(
                status_code=403,
                detail="User is not a member of the requested company",
            )

        company_use_case = self.get_company_use_case_factory(
            company_id=data.company_id,
        )
        try:
            company_use_case.run()
        except StopUseCaseException as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if not company_use_case.data:
            raise HTTPException(status_code=404, detail="Company not found")

        payload = {
            "sub": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "company_id": data.company_id,
            "company_ids": membership_ids,
            "role": current_user.role,
            "is_superuser": current_user.is_superuser,
        }
        token = create_access_token(payload)
        cache_user_from_payload(payload)

        return {
            "access_token": token,
            "token_type": "bearer",
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "company_id": data.company_id,
            "company_ids": membership_ids,
            "role": current_user.role,
            "is_superuser": current_user.is_superuser,
        }

    @router.post(
        "/logout",
        response_model=MessageResponse,
        summary="Logout",
        description="Invalidates the current user's Redis session cache.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
        },
    )
    def logout(self, current_user: CachedUser = CurrentUserDep):
        invalidate_user_session(current_user.id)
        return {"detail": "Logged out successfully"}

    @router.get(
        "/me",
        response_model=UserLoginResponse,
        summary="Current session",
        description="Returns the authenticated user profile from the JWT session.",
        responses={
            401: {"model": ErrorResponse, "description": "Missing or invalid JWT."},
        },
    )
    def me(self, current_user: CachedUser = CurrentUserDep):
        return {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "company_id": current_user.company_id,
            "company_ids": list(current_user.company_ids or []),
            "role": current_user.role,
            "is_superuser": current_user.is_superuser,
        }
