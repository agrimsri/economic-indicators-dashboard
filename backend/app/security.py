import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Response, status

from app.config import settings

logger = logging.getLogger(__name__)

# Argon2id password hasher
_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # 64 MB
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


# ==========================================
# JWT ACCESS TOKENS (HS256)
# ==========================================

def create_access_token(user_id: int, username: str, role: str = "viewer") -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.jwt_access_ttl_min)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "sub", "jti"]}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "TOKEN_EXPIRED", "message": "Access token has expired"}}
        ) from None
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_TOKEN", "message": f"Invalid token: {e}"}}
        ) from e


# ==========================================
# REFRESH TOKENS (Opaque 256-bit + SHA-256 Hash)
# ==========================================

def generate_refresh_token() -> str:
    # 32 bytes = 256 bits of cryptographic entropy
    return secrets.token_hex(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def set_refresh_cookie(response: Response, raw_token: str) -> None:
    max_age = settings.jwt_refresh_ttl_days * 24 * 60 * 60
    response.set_cookie(
        key="refresh_token",
        value=raw_token,
        max_age=max_age,
        expires=max_age,
        path="/auth",
        domain=settings.cookie_domain if settings.cookie_domain != "localhost" else None,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/auth",
        domain=settings.cookie_domain if settings.cookie_domain != "localhost" else None,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
