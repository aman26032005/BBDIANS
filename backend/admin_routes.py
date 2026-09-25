from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from time import monotonic

from .database import get_db
from .models import Confession
from .admin_auth import (
    verify_admin_login,
    create_admin_token,
    verify_admin_token
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# -----------------------------
# LOGIN RATE LIMIT
# -----------------------------

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 minutes

failed_attempts = {}


def check_login_rate_limit(client_ip: str):
    now = monotonic()

    record = failed_attempts.get(client_ip)

    if not record:
        return

    attempts, first_attempt, locked_until = record

    if locked_until > now:
        remaining = int(locked_until - now)

        raise HTTPException(
            status_code=429,
            detail=f"Too many failed login attempts. Try again in {remaining} seconds."
        )

    # Reset old records
    if now - first_attempt > LOCKOUT_SECONDS:
        failed_attempts.pop(client_ip, None)


def record_failed_login(client_ip: str):
    now = monotonic()

    record = failed_attempts.get(client_ip)

    if not record:
        failed_attempts[client_ip] = (
            1,
            now,
            0
        )
        return

    attempts, first_attempt, locked_until = record

    # Reset expired window
    if now - first_attempt > LOCKOUT_SECONDS:
        failed_attempts[client_ip] = (
            1,
            now,
            0
        )
        return

    attempts += 1

    if attempts >= MAX_LOGIN_ATTEMPTS:
        failed_attempts[client_ip] = (
            attempts,
            first_attempt,
            now + LOCKOUT_SECONDS
        )
    else:
        failed_attempts[client_ip] = (
            attempts,
            first_attempt,
            0
        )


def clear_failed_logins(client_ip: str):
    failed_attempts.pop(client_ip, None)


# -----------------------------
# ADMIN LOGIN
# -----------------------------

class AdminLoginRequest(BaseModel):
    password: str


@router.post("/login")
def admin_login(
    data: AdminLoginRequest,
    request: Request
):

    client_ip = request.client.host if request.client else "unknown"

    check_login_rate_limit(client_ip)

    if not verify_admin_login(data.password):

        record_failed_login(client_ip)

        raise HTTPException(
            status_code=401,
            detail="Invalid admin password"
        )

    clear_failed_logins(client_ip)

    token = create_admin_token()

    return {
        "message": "Admin login successful",
        "access_token": token,
        "token_type": "bearer"
    }


# -----------------------------
# GET ALL CONFESSIONS
# -----------------------------

@router.get("/confessions")
def get_all_confessions(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):

    confessions = (
        db.query(Confession)
        .order_by(Confession.created_at.desc())
        .all()
    )

    return [
        {
            "id": confession.id,
            "message": confession.message,
            "created_at": confession.created_at,
            "is_read": confession.is_read
        }
        for confession in confessions
    ]


# -----------------------------
# MARK AS READ
# -----------------------------

@router.put("/confessions/{confession_id}/read")
def mark_confession_as_read(
    confession_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):

    confession = (
        db.query(Confession)
        .filter(
            Confession.id == confession_id
        )
        .first()
    )

    if not confession:
        raise HTTPException(
            status_code=404,
            detail="Confession not found"
        )

    confession.is_read = True

    db.commit()
    db.refresh(confession)

    return {
        "message": "Confession marked as read",
        "confession_id": confession.id
    }


# -----------------------------
# DELETE CONFESSION
# -----------------------------

@router.delete("/confessions/{confession_id}")
def delete_confession(
    confession_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):

    confession = (
        db.query(Confession)
        .filter(
            Confession.id == confession_id
        )
        .first()
    )

    if not confession:
        raise HTTPException(
            status_code=404,
            detail="Confession not found"
        )

    db.delete(confession)
    db.commit()

    return {
        "message": "Confession deleted successfully",
        "confession_id": confession_id
    }