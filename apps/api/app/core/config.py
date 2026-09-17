from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fsociety API"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://fsociety:fsociety@localhost:5432/fsociety"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days, admin-only tool for now

    frontend_url: str = "http://localhost:5173"

    upload_dir: str = "/tmp/fsociety/uploads"
    max_upload_size_mb: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
