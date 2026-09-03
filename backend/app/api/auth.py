"""FR-01: register/login (email+password) + Google OAuth sync."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.base import get_db
from app.models.plan import Plan
from app.models.user import User
from app.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.google_oauth import GoogleTokenError, verify_google_id_token

router = APIRouter()

DEFAULT_PLAN_NAME = "Free"


def _default_plan_id(db: Session):
    plan = db.execute(select(Plan).where(Plan.name == DEFAULT_PLAN_NAME)).scalar_one_or_none()
    return plan.id if plan else None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email sudah terdaftar — silakan login.")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        plan_id=_default_plan_id(db),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id), user=UserOut.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    invalid = HTTPException(status.HTTP_401_UNAUTHORIZED, "Email atau password salah.")
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if user is None or user.password_hash is None:
        raise invalid
    if not verify_password(payload.password, user.password_hash):
        raise invalid

    return TokenResponse(
        access_token=create_access_token(user.id), user=UserOut.model_validate(user)
    )


@router.post("/oauth/google", response_model=TokenResponse)
def google_oauth(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    try:
        claims = verify_google_id_token(payload.id_token)
    except GoogleTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

    google_id = claims["sub"]
    email = claims.get("email")
    name = claims.get("name", email or "")

    user = db.execute(select(User).where(User.google_id == google_id)).scalar_one_or_none()
    if user is None and email:
        # Same email already registered via password — link the Google identity to it.
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if user is None:
        user = User(email=email, name=name, google_id=google_id, plan_id=_default_plan_id(db))
        db.add(user)
    elif user.google_id is None:
        user.google_id = google_id

    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id), user=UserOut.model_validate(user)
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
