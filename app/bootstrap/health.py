from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, Field
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.cache_utils.user_cache import redis_client
from app.core.database import engine

router = APIRouter(tags=["Health"])


class HealthChecks(BaseModel):
    database: bool = Field(description="PostgreSQL connectivity.")
    redis: bool = Field(description="Redis connectivity.")


class HealthResponse(BaseModel):
    status: str = Field(description="Overall status: ok or degraded.")
    checks: HealthChecks

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "checks": {"database": True, "redis": True},
            }
        }
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Verifies PostgreSQL and Redis connectivity. " "Used by Docker healthchecks."
    ),
)
def health_check(response: Response) -> dict:
    checks = {
        "database": False,
        "redis": False,
    }

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = True
    except SQLAlchemyError:
        pass

    try:
        checks["redis"] = bool(redis_client.ping())
    except RedisError:
        pass

    healthy = all(checks.values())
    response.status_code = 200 if healthy else 503

    return {
        "status": "ok" if healthy else "degraded",
        "checks": checks,
    }
