from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv

from app.adapters.container import Container
from app.application.dtos.user_dto import UserLoginDTO
from app.core.auth.deps import CanCreateUserDep, CompanyIdDep, CurrentUserDep
from app.core.cache_utils.user_cache import CachedUser, invalidate_user_session
from app.domain.use_cases.exceptions import StopUseCaseException
from app.presentation.api.v1.schemas.common import ErrorResponse, MessageResponse
from app.presentation.api.v1.schemas.user import (
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
    ):
        self.authenticate_user_use_case_factory = authenticate_user_use_case_factory
        self.create_user_use_case_factory = create_user_use_case_factory

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
            "Authenticates with email and password. Returns a JWT and caches "
            "the session in Redis for 24 hours."
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
