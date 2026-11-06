from uuid import uuid4

import jwt
import pytest
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_token,
)


@pytest.fixture(autouse=True)
def use_test_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-key-with-at-least-32-bytes")


def test_production_configuration_rejects_placeholder_or_short_secrets() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production")
    with pytest.raises(ValidationError):
        Settings(environment="production", jwt_secret_key="short")


def test_vercel_production_configuration_rejects_development_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="development", vercel_env="production")


def test_access_token_has_explicit_type_and_required_claims() -> None:
    user_id = str(uuid4())
    session_id = uuid4()
    token = create_access_token(user_id, session_id)

    claims = decode_access_token(token)
    assert claims is not None
    assert claims["sub"] == user_id
    assert claims["sid"] == str(session_id)
    assert claims["typ"] == "access"
    assert claims["jti"]
    assert claims["iat"] < claims["exp"]


def test_refresh_token_is_separate_and_has_configured_lifetime() -> None:
    user_id = str(uuid4())
    session_id = uuid4()
    token_id = uuid4()
    token = create_refresh_token(user_id, session_id, token_id)

    claims = decode_token(token, "refresh")
    assert claims is not None
    assert claims["sub"] == user_id
    assert claims["jti"] == str(token_id)
    assert claims["typ"] == "refresh"
    assert claims["exp"] - claims["iat"] == settings.refresh_token_expire_days * 24 * 60 * 60
    assert decode_access_token(token) is None


def test_token_decoder_rejects_missing_required_claims() -> None:
    malformed = jwt.encode({"sub": str(uuid4())}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    assert decode_access_token(malformed) is None
