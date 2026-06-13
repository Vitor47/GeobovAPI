from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):
    detail: str = Field(description="Human-readable status message.")

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Logged out successfully"}}
    )


class ErrorResponse(BaseModel):
    detail: str = Field(description="Error description.")

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Invalid credentials"}}
    )
