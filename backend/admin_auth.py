import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from dotenv import load_dotenv
from fastapi import Header, HTTPException


# Load variables from .env
load_dotenv()


password_hasher = PasswordHasher()


# -----------------------------
# SECURITY SETTINGS
# -----------------------------

ADMIN_PASSWORD_HASH = os.getenv(
    "BBDIANS_ADMIN_PASSWORD_HASH"
)

JWT_SECRET = os.getenv(
    "BBDIANS_JWT_SECRET"
)

JWT_ALGORITHM = "HS256"

TOKEN_EXPIRE_MINUTES = 60


# Make sure required secrets exist
if not ADMIN_PASSWORD_HASH:
    raise RuntimeError(
        "BBDIANS_ADMIN_PASSWORD_HASH is missing from .env"
    )

if not JWT_SECRET:
    raise RuntimeError(
        "BBDIANS_JWT_SECRET is missing from .env"
    )


# -----------------------------
# ADMIN PASSWORD VERIFICATION
# -----------------------------

def verify_admin_login(password: str) -> bool:
    """Verify the admin password."""

    if not password:
        return False

    try:
        return password_hasher.verify(
            ADMIN_PASSWORD_HASH,
            password
        )

    except Exception:
        return False


# -----------------------------
# CREATE JWT TOKEN
# -----------------------------

def create_admin_token() -> str:
    """Create a short-lived JWT for the admin."""

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "role": "admin",
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


# -----------------------------
# VERIFY JWT TOKEN
# -----------------------------

def verify_admin_token(
    authorization: str = Header(default="")
):
    """Verify the JWT supplied by the admin dashboard."""

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required"
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        if payload.get("role") != "admin":
            raise HTTPException(
                status_code=401,
                detail="Invalid admin role"
            )

        return True

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Admin session expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )