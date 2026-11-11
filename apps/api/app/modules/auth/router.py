from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession, oauth2_scheme
from app.core.rate_limit import limiter
from app.core.security import decode_token
from app.modules.auth.models import AuthSession, User
from app.modules.auth.schemas import (
    RefreshRequest,
    TokenOut,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.modules.auth.service import (
    authenticate,
    get_user_by_email,
    issue_token_pair,
    register_user,
    user_to_out_dict,
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def register(request: Request, data: UserRegister, db: DbSession):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="An account already exists for this email")
    try:
        user = register_user(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account already exists for this email") from None
    return user_to_out_dict(user)


@router.post("/login", response_model=TokenOut)
@limiter.limit("5/minute")
def login(request: Request, data: UserLogin, db: DbSession):
    user = authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return issue_token_pair(db, user)


@router.post("/refresh", response_model=TokenOut)
def refresh_token(data: RefreshRequest, db: DbSession):
    claims = decode_token(data.refresh_token, "refresh")
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token is invalid or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not claims:
        raise invalid

    session_id = UUID(claims["sid"])
    user_id = UUID(claims["sub"])
    auth_session = db.scalar(
        select(AuthSession).where(AuthSession.id == session_id).with_for_update()
    )
    now = datetime.now(UTC)
    session_expires_at = auth_session.expires_at if auth_session else now
    if session_expires_at.tzinfo is None:
        session_expires_at = session_expires_at.replace(tzinfo=UTC)
    if (
        not auth_session
        or auth_session.user_id != user_id
        or auth_session.revoked_at is not None
        or session_expires_at <= now
        or auth_session.refresh_jti != claims["jti"]
    ):
        raise invalid

    user = db.get(User, user_id)
    if not user or not user.is_active:
        auth_session.revoked_at = now
        db.commit()
        raise invalid

    return issue_token_pair(db, user, revoke_session=auth_session)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: DbSession,
    current_user: CurrentUser,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(oauth2_scheme)],
):
    if credentials:
        claims = decode_token(credentials.credentials, "access")
        if claims:
            auth_session = db.get(AuthSession, UUID(claims["sid"]))
            if auth_session and auth_session.user_id == current_user.id and not auth_session.revoked_at:
                auth_session.revoked_at = datetime.now(UTC)
                db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserOut)
def me(current_user: CurrentUser):
    return user_to_out_dict(current_user)
