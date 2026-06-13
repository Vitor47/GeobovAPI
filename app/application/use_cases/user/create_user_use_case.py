from dataclasses import dataclass, field

from app.application.dtos.user_dto import UserCreateDTO, UserResponseDTO
from app.application.steps.user import CreateUserStep
from app.domain.repositories.user_repository_abstract import (
    UserRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class CreateUserUseCase(BaseUseCase):
    repository: UserRepositoryAbstract
    payload: UserCreateDTO
    data: UserResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[CreateUserStep])
