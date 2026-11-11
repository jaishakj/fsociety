from functools import lru_cache
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient, PyJWKClientError

from app.core.config import settings

bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_keys=True, lifespan=3600)


def get_clerk_claims(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict[str, Any]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A valid customer session is required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise unauthorized
    if not settings.clerk_jwks_url or not settings.clerk_issuer:
        raise HTTPException(status_code=503, detail="Customer authentication is not configured")

    try:
        signing_key = _jwks_client(settings.clerk_jwks_url).get_signing_key_from_jwt(
            credentials.credentials
        )
        claims = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.clerk_issuer,
            options={"require": ["exp", "iat", "sub", "iss"]},
        )
    except (jwt.PyJWTError, PyJWKClientError, ValueError):
        raise unauthorized from None

    allowed_parties = {
        party.strip().rstrip("/")
        for party in settings.clerk_authorized_parties.split(",")
        if party.strip()
    }
    azp = claims.get("azp")
    if not allowed_parties or not isinstance(azp, str) or azp.rstrip("/") not in allowed_parties:
        raise unauthorized
    if not isinstance(claims.get("sub"), str) or not claims["sub"].startswith("user_"):
        raise unauthorized
    return claims


ClerkClaims = Annotated[dict[str, Any], Depends(get_clerk_claims)]
