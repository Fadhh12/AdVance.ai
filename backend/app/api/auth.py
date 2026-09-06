"""FR-01: register/login (email+password) + Google OAuth sync. Also `POST /auth/guest`
(Phase 6R) — an anonymous account so the frontend can land straight on the workspace
without a visible login form; see app/(workspace)/layout.tsx.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
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
OWNER_PLAN_NAME = "Unlimited"  # seeded in b7b7f3d31c32_seed_unlimited_plan.py


def _plan_id_for_email(db: Session, email: str | None) -> uuid.UUID | None:
    """The Unlimited plan is never self-serve — it's assigned only when the
    registering/logging-in email matches OWNER_EMAIL in .env (Phase 6R). Everyone
    else, including guests, gets the normal Free plan.
    """
    owner_email = get_settings().owner_email
    if email and owner_email and email.strip().lower() == owner_email.strip().lower():
        owner_plan = db.execute(
            select(Plan).where(Plan.name == OWNER_PLAN_NAME)
        ).scalar_one_or_none()
        if owner_plan is not None:
            return owner_plan.id

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
        plan_id=_plan_id_for_email(db, payload.email),
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
        user = User(
            email=email, name=name, google_id=google_id, plan_id=_plan_id_for_email(db, email)
        )
        db.add(user)
    elif user.google_id is None:
        user.google_id = google_id

    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id), user=UserOut.model_validate(user)
    )


@router.post("/guest", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def guest(db: Session = Depends(get_db)):
    """Anonymous account, no form to fill (Phase 6R) — always the Free plan (a
    fabricated email can never match `OWNER_EMAIL`, so `_plan_id_for_email` always
    falls through to Free here). Each call creates a *new* guest row; the frontend is
    responsible for persisting the returned token client-side so a page reload doesn't
    spawn a fresh guest (and fresh quota) every time.
    """
    # Note: not `.local` — email-validator (used by Pydantic's EmailStr in UserOut)
    # rejects that as a reserved special-use domain.
    guest_email = f"guest+{uuid.uuid4().hex}@guest.advanceai.app"
    user = User(email=guest_email, name="Tamu", plan_id=_plan_id_for_email(db, guest_email))
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id), user=UserOut.model_validate(user)
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
