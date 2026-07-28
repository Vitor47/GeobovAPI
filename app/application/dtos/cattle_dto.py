from dataclasses import dataclass
from datetime import datetime

from app.domain.enums.cattle_enum import GenderEnum


@dataclass
class CattleCreateDTO:
    tag: str
    name: str
    company_id: int
    description: str | None = None
    birth_date: datetime | None = None
    weight: float | None = None
    breed: str | None = None
    gender: GenderEnum | None = None
    color: str | None = None
    notes: str | None = None


@dataclass
class CattleUpdateDTO:
    tag: str | None = None
    name: str | None = None
    description: str | None = None
    birth_date: datetime | None = None
    weight: float | None = None
    breed: str | None = None
    gender: GenderEnum | None = None
    color: str | None = None
    notes: str | None = None
    is_active: bool | None = None


@dataclass
class CattleResponseDTO:
    id: int
    tag: str
    name: str
    company_id: int
    is_active: bool
    description: str | None = None
    birth_date: datetime | None = None
    weight: float | None = None
    breed: str | None = None
    gender: GenderEnum | None = None
    color: str | None = None
    notes: str | None = None
