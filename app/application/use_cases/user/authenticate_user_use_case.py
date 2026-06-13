from dataclasses import dataclass, field

from app.application.dtos.user_dto import LoginResponseDTO
from app.application.steps.user import AuthenticateUserStep
from app.domain.repositories.user_repository_abstract import (
    UserRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class AuthenticateUserUseCase(BaseUseCase):
    repository: UserRepositoryAbstract
    email: str
    password: str
    data: LoginResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(
            steps=[
                AuthenticateUserStep,
            ]
        )
