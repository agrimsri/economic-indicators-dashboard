import pytest
from fastapi import HTTPException

from app.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_argon2id_hashing():
    raw_password = "super_secure_password_123"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_access_token_creation_and_decoding():
    token = create_access_token(user_id=42, username="test_evaluator", role="evaluator")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["username"] == "test_evaluator"
    assert payload["role"] == "evaluator"
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("not.a.valid.jwt.token")
    assert exc_info.value.status_code == 401


def test_refresh_token_entropy_and_hashing():
    token1 = generate_refresh_token()
    token2 = generate_refresh_token()
    assert token1 != token2
    assert len(token1) == 64  # 32 bytes hex = 64 characters

    h1 = hash_refresh_token(token1)
    h2 = hash_refresh_token(token1)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex string
