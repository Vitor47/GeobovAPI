from datetime import date
from typing import TypedDict

from app.domain.enums.role_enum import RoleEnum


class LoginResponseDTO(TypedDict):
    access_token: str
    token_type: str
    id: int
    email: str
    full_name: str
    company_id: int | None
    role: str | None
    is_superuser: bool


class UserCreateDTO:
    def __init__(
        self,
        full_name: str,
        birth_date: date,
        email: str,
        password: str,
        company_id: int,
        role: RoleEnum,
    ):
        self.full_name = full_name
        self.birth_date = birth_date
        self.email = email
        self.password = password
        self.company_id = company_id
        self.role = role


class UserResponseDTO:
    def __init__(
        self,
        id: int,
        full_name: str,
        birth_date: date,
        email: str,
        company_id: int,
        role: RoleEnum,
    ):
        self.id = id
        self.full_name = full_name
        self.birth_date = birth_date
        self.email = email
        self.company_id = company_id
        self.role = role


class UserLoginDTO:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
