from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.modules.auth.schemas import TokenOut, UserLogin, UserOut, UserRegister
from app.modules.auth.service import (
    authenticate,
    get_user_by_email,
    issue_token,
    register_user,
    user_to_out_dict,
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: DbSession):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = register_user(db, data)
    return user_to_out_dict(user)


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: DbSession):
    user = authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return TokenOut(access_token=issue_token(user))


@router.get("/me", response_model=UserOut)
def me(current_user: CurrentUser):
    return user_to_out_dict(current_user)
