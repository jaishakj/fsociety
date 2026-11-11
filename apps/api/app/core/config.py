from functools import lru_cache
from pathlib import Path
from tempfile import gettempdir

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fsociety API"
    environment: str = "development"
    vercel_env: str | None = None

    database_url: str = "postgresql+psycopg://fsociety:fsociety@localhost:5432/fsociety"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    rate_limit_storage_uri: str = "memory://"

    frontend_url: str = "http://localhost:5173"

    # Clerk verifies customer identity; these public verification settings are
    # deliberately separate from the legacy JWT used by the admin interface.
    clerk_jwks_url: str | None = None
    clerk_issuer: str | None = None
    clerk_authorized_parties: str = ""
    customer_data_owner_email: str | None = None

    upload_dir: str = str(Path(gettempdir()) / "fsociety" / "uploads")
    max_upload_size_mb: int = 4
    blob_store_id: str | None = None

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in {"development", "dev", "test"} and self.vercel_env in {
            None,
            "development",
        }

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if not self.is_development:
            secret = self.jwt_secret_key.strip()
            if (
                secret in {"change-me", "replace-with-a-long-random-secret"}
                or secret.lower().startswith("replace-")
                or len(secret.encode("utf-8")) < 32
            ):
                raise ValueError("JWT_SECRET_KEY must contain at least 32 bytes outside development")
        if self.access_token_expire_minutes < 1 or self.refresh_token_expire_days < 1:
            raise ValueError("Token expiration settings must be positive")
        if self.max_upload_size_mb < 1:
            raise ValueError("MAX_UPLOAD_SIZE_MB must be positive")
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
