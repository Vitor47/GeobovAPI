from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.cattle_enum import GenderEnum


class CattleCreate(BaseModel):
    tag: str = Field(description="Unique ear tag / identifier within the farm.")
    name: str = Field(description="Friendly cattle name.")
    description: str | None = None
    birth_date: datetime | None = None
    weight: float | None = None
    breed: str | None = None
    gender: GenderEnum | None = None
    color: str | None = None
    notes: str | None = Field(default=None, description="Initial observation notes.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tag": "BR-001",
                "name": "Mimosa",
                "breed": "Nelore",
                "gender": "female",
                "notes": "Bought in 2026 auction",
            }
        }
    )


class CattleUpdate(BaseModel):
    tag: str | None = None
    name: str | None = None
    description: str | None = None
    birth_date: datetime | None = None
    weight: float | None = None
    breed: str | None = None
    gender: GenderEnum | None = None
    color: str | None = None
    notes: str | None = Field(
        default=None,
        description="Observation / notes from the farmer app.",
    )
    is_active: bool | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notes": "Limping on left rear leg",
                "weight": 420.5,
            }
        }
    )


class CattleResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
