import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.migrator import run_migrations
from app.db.pool import close_db_pool, init_db_pool
from app.db.queries import create_user
from app.main import app
from app.security import hash_password


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await run_migrations()
    await init_db_pool()
    # Seed a known test user
    hashed = hash_password("test_pass_123")
    await create_user(username="testuser", password_hash=hashed, role="viewer")
    yield
    await close_db_pool()


@pytest.mark.asyncio
async def test_auth_full_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Invalid login
        bad_login = await ac.post("/auth/login", json={"username": "testuser", "password": "wrongpassword"})
        assert bad_login.status_code == 401
        assert "INVALID_CREDENTIALS" in bad_login.text

        # 2. Valid login
        login_res = await ac.post("/auth/login", json={"username": "testuser", "password": "test_pass_123"})
        assert login_res.status_code == 200
        data = login_res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        access_token = data["access_token"]
        assert "refresh_token" in login_res.cookies
        refresh_cookie = login_res.cookies["refresh_token"]

        # 3. Access protected /auth/me
        me_res = await ac.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert me_res.status_code == 200
        user_data = me_res.json()
        assert user_data["username"] == "testuser"
        assert user_data["role"] == "viewer"

        # 4. Access protected without token
        unauth_res = await ac.get("/auth/me")
        assert unauth_res.status_code == 401

        # 5. Refresh token rotation
        refresh_res = await ac.post("/auth/refresh", cookies={"refresh_token": refresh_cookie})
        assert refresh_res.status_code == 200
        new_data = refresh_res.json()
        assert "access_token" in new_data
        new_access_token = new_data["access_token"]
        assert new_access_token and len(new_access_token) > 0
        assert "refresh_token" in refresh_res.cookies
        new_refresh_cookie = refresh_res.cookies["refresh_token"]
        assert new_refresh_cookie != refresh_cookie  # Must be rotated!

        # 6. Replay attack with old revoked refresh token MUST fail
        replay_res = await ac.post("/auth/refresh", cookies={"refresh_token": refresh_cookie})
        assert replay_res.status_code == 401
        assert "TOKEN_REVOKED" in replay_res.text

        # 7. Logout with active token
        logout_res = await ac.post("/auth/logout", cookies={"refresh_token": new_refresh_cookie})
        assert logout_res.status_code == 200

        # 8. Post-logout refresh MUST fail
        post_logout_res = await ac.post("/auth/refresh", cookies={"refresh_token": new_refresh_cookie})
        assert post_logout_res.status_code == 401
