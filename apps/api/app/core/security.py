from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(
    subject: str,
    session_id: UUID,
    expires_minutes: int | None = None,
) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(
        minutes=expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "sid": str(session_id),
        "iat": now,
        "exp": expire,
        "jti": str(uuid4()),
        "typ": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, session_id: UUID, token_id: UUID) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "sid": str(session_id),
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
        "jti": str(token_id),
        "typ": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "sid", "iat", "exp", "jti", "typ"]},
        )
        if payload.get("typ") != expected_type:
            return None
        UUID(payload["sid"])
        UUID(payload["jti"])
        if not isinstance(payload.get("sub"), str) or not payload["sub"]:
            return None
        return payload
    except jwt.PyJWTError:
        return None
    except (KeyError, TypeError, ValueError):
        return None


def decode_access_token(token: str) -> dict | None:
    return decode_token(token, "access")
