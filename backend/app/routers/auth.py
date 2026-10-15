from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.config import settings
from app.db.queries import (
    create_refresh_token,
    get_refresh_token_by_hash,
    get_user_by_id,
    get_user_by_username,
    revoke_refresh_token,
)
from app.deps import get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.security import (
    clear_refresh_cookie,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    set_refresh_cookie,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    response: Response,
):
    user = await get_user_by_username(req.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"}},
        )

    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"}},
        )

    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "USER_INACTIVE", "message": "Account is disabled"}},
        )

    # Generate Access Token
    access_token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"]
    )

    # Generate & Rotate Refresh Token
    raw_refresh = generate_refresh_token()
    token_hash = hash_refresh_token(raw_refresh)
    expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_ttl_days)
    await create_refresh_token(user["id"], token_hash, expires_at)

    set_refresh_cookie(response, raw_refresh)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_ttl_min * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    refresh_token: str | None = Cookie(None),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "MISSING_REFRESH_TOKEN", "message": "Refresh token cookie missing"}},
        )

    token_hash = hash_refresh_token(refresh_token)
    stored_token = await get_refresh_token_by_hash(token_hash)

    if not stored_token:
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_REFRESH_TOKEN", "message": "Refresh token not found"}},
        )

    if stored_token.get("revoked_at") is not None:
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "TOKEN_REVOKED", "message": "Refresh token has been revoked"}},
        )

    now = datetime.now(UTC)
    token_expires = stored_token["expires_at"]
    if token_expires.tzinfo is None:
        token_expires = token_expires.replace(tzinfo=UTC)

    if token_expires < now:
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "TOKEN_EXPIRED", "message": "Refresh token has expired"}},
        )

    # Token rotation: revoke used token immediately
    await revoke_refresh_token(token_hash)

    # Fetch user
    user = await get_user_by_id(stored_token["user_id"])
    if not user or not user.get("is_active"):
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "USER_INACTIVE", "message": "User inactive or deleted"}},
        )

    # Issue new access token
    new_access = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"]
    )

    # Issue new refresh token
    new_raw_refresh = generate_refresh_token()
    new_token_hash = hash_refresh_token(new_raw_refresh)
    new_expires_at = now + timedelta(days=settings.jwt_refresh_ttl_days)
    await create_refresh_token(user["id"], new_token_hash, new_expires_at)

    set_refresh_cookie(response, new_raw_refresh)

    return TokenResponse(
        access_token=new_access,
        token_type="bearer",
        expires_in=settings.jwt_access_ttl_min * 60,
    )


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(None),
):
    if refresh_token:
        token_hash = hash_refresh_token(refresh_token)
        await revoke_refresh_token(token_hash)

    clear_refresh_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict[str, Any] = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user["role"],
        is_active=current_user["is_active"],
    )
