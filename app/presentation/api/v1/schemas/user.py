from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(description="Unique user email.")
    password: str = Field(
        min_length=8, description="Plain-text password (hashed server-side)."
    )
    company_id: int | None = Field(
        default=None,
        description="Default farm for the new user (also added as membership).",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "farmer@example.com",
                "password": "dev123456",
            }
        }
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    company_id: int | None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "email": "farmer@example.com",
                "company_id": 1,
            }
        },
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(description="Registered user email.")
    password: str = Field(description="Account password.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@example.com",
                "password": "changeme",
            }
        }
    )


class UserLoginResponse(BaseModel):
    access_token: str | None = Field(default=None, description="JWT bearer token.")
    token_type: str | None = Field(default=None, examples=["bearer"])
    id: int | None = None
    email: str | None = None
    full_name: str | None = None
    company_id: int | None = Field(
        default=None,
        description="Default farm used when X-Company-Id is omitted.",
    )
    company_ids: list[int] | None = Field(
        default=None,
        description="Farms the user belongs to (memberships).",
    )
    role: str | None = Field(
        default=None, description="Role name (admin, manager, viewer)."
    )
    is_superuser: bool | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "id": 1,
                "email": "farmer@example.com",
                "full_name": "Joao Fazendeiro",
                "company_id": 1,
                "company_ids": [1, 2],
                "role": "manager",
                "is_superuser": False,
            }
        },
    )
