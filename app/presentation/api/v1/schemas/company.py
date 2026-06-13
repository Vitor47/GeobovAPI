from pydantic import BaseModel, ConfigDict, Field

from app.presentation.api.v1.schemas.user import UserResponse


class CompanyCreate(BaseModel):
    name: str = Field(description="Company or farm display name.")

    model_config = ConfigDict(json_schema_extra={"example": {"name": "Dev Farm"}})


class CompanyResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"id": 1, "name": "Dev Farm"}},
    )


class CompanyWithUsers(BaseModel):
    id: int
    name: str
    users: list[UserResponse] = []

    model_config = ConfigDict(from_attributes=True)
