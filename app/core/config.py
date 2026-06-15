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

    APP_PORT: int

    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_FULL_NAME: str


settings = Settings()
