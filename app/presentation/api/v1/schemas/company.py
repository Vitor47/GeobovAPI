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


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [{"id": 1, "name": "Fazenda São João"}],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "has_more": True,
            }
        }
    )


class CompanyWithUsers(BaseModel):
    id: int
    name: str
    users: list[UserResponse] = []

    model_config = ConfigDict(from_attributes=True)
