from dataclasses import dataclass
from datetime import datetime

from app.domain.enums.cattle_enum import GenderEnum


@dataclass
class CattleCreateDTO:
    tag: str
    name: str
    description: str | None
    birth_date: datetime | None
    weight: float | None
    breed: str | None
    gender: GenderEnum | None
    color: str | None
    notes: str | None
    company_id: int


@dataclass
class CattleDataCreateDTO:
    cattle_id: int
    lat: float
    lon: float
    movement: float
    temperature: float


@dataclass
class CattleResponseDTO:
    id: int
    tag: str
    company_id: int
