from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import AuthSession, User, UserRole, UserRoleAssignment
from app.modules.auth.schemas import UserRegister


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, data: UserRegister, make_admin: bool = False) -> User:
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
    )
    role = UserRole.ADMIN if make_admin else UserRole.USER
    user.roles.append(UserRoleAssignment(role=role))

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user


def issue_token_pair(
    db: Session,
    user: User,
    *,
    revoke_session: AuthSession | None = None,
) -> dict[str, str | int]:
    session_id = uuid4()
    refresh_jti = uuid4()
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    session = AuthSession(
        id=session_id,
        user_id=user.id,
        refresh_jti=str(refresh_jti),
        expires_at=expires_at,
    )
    if revoke_session is not None:
        revoke_session.revoked_at = datetime.now(UTC)
    db.add(session)
    db.commit()
    return {
        "access_token": create_access_token(str(user.id), session_id),
        "refresh_token": create_refresh_token(str(user.id), session_id, refresh_jti),
        "expires_in": settings.access_token_expire_minutes * 60,
    }


def user_to_out_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "roles": [assignment.role.value for assignment in user.roles],
    }
