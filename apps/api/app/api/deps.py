from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.auth.models import AuthSession, User, UserRole

oauth2_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(oauth2_scheme),
    ] = None,
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise credentials_error
    claims = decode_access_token(credentials.credentials)
    if not claims:
        raise credentials_error

    try:
        user_id = UUID(claims["sub"])
        session_id = UUID(claims["sid"])
    except ValueError:
        raise credentials_error from None

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_error

    auth_session = db.get(AuthSession, session_id)
    session_expired = False
    if auth_session:
        session_expires_at = auth_session.expires_at
        if session_expires_at.tzinfo is None:
            session_expires_at = session_expires_at.replace(tzinfo=UTC)
        session_expired = session_expires_at <= datetime.now(UTC)

    if (
        not auth_session
        or auth_session.user_id != user.id
        or auth_session.revoked_at is not None
        or session_expired
    ):
        raise credentials_error

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(current_user: CurrentUser) -> User:
    roles = {assignment.role for assignment in current_user.roles}
    if UserRole.ADMIN not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


AdminUser = Annotated[User, Depends(require_admin)]
