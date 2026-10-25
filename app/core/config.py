from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    SESSION_CACHE_TTL_SECONDS: int

    MONGO_URL: str
    MONGO_DB_NAME: str = "cow_track"
    TELEMETRY_RAW_RETENTION_DAYS: int = 30
    TELEMETRY_HISTORY_INTERVAL_MINUTES: int = 30

    # local | development → docs on; production → docs off (override with DOCS_ENABLED)
    APP_ENV: str = "local"
    DOCS_ENABLED: bool | None = None
    # Restrict by reverse-proxy IP allowlist in production; or set ADMIN_ENABLED=false
    ADMIN_ENABLED: bool = True

    APP_PORT: int

    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_FULL_NAME: str

    LOGIN_MAX_ATTEMPTS: int = 10
    LOGIN_ATTEMPT_WINDOW_SECONDS: int = 900
    INGEST_MAX_REQUESTS: int = 120
    INGEST_WINDOW_SECONDS: int = 60

    @property
    def is_docs_enabled(self) -> bool:
        if self.DOCS_ENABLED is not None:
            return self.DOCS_ENABLED
        return self.APP_ENV.lower() in {"local", "development", "dev"}


settings = Settings()
