from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.presentation.api.v1.schemas.user import UserResponse


class CompanyListQuery(BaseModel):
    """Query string for GET /companies."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    q: str | None = Field(
        default=None,
        max_length=80,
        pattern=r"^[0-9A-Za-zÀ-ÿ]+(?:[ '\-][0-9A-Za-zÀ-ÿ]+)*$",
        description=(
            "Farm name filter. Letters, numbers, spaces, apostrophes and hyphens."
        ),
        examples=["Fazenda São João"],
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("q", mode="before")
    @classmethod
    def blank_query_is_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


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
