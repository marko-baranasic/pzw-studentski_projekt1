from freezegun import freeze_time

from app.core.jwt import create_refresh_token
from tests.utils import PASSWORD, auth_header, make_user


async def test_login_returns_tokens(client, session):
    await make_user(session, "ana@test.hr")

    response = await client.post(
        "/auth/login", json={"username": "ana@test.hr", "password": PASSWORD}
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_wrong_password_and_unknown_user_get_same_401(client, session):
    await make_user(session, "ana@test.hr")

    wrong_password = await client.post(
        "/auth/login", json={"username": "ana@test.hr", "password": "kriva-lozinka"}
    )
    unknown_user = await client.post(
        "/auth/login", json={"username": "nitko@test.hr", "password": PASSWORD}
    )

    assert wrong_password.status_code == 401
    assert wrong_password.json()["code"] == "invalid_credentials"
    assert wrong_password.json() == unknown_user.json()


async def test_me_returns_user_without_password_hash(client, session):
    user =  await make_user(session, "ana@test.hr")

    response = await client.get("/auth/me", headers=auth_header(user))

    assert response.status_code == 200
    assert response.json()["username"] == "ana@test.hr"
    assert "password_hash" not in response.json()


async def test_me_without_token_is_401(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


async def test_me_rejects_refresh_token(client, session):
    user = await make_user(session, "ana@test.hr")
    headers = {"Authorization": f"Bearer {create_refresh_token(user.id)}"}

    response = await client.get("/auth/me", headers=headers)

    assert response.status_code == 401


async def test_expired_access_token_is_rejected(client, session):
    user = await make_user(session, "ana@test.hr")
    # Token izdan u podne vrijedi 15 minuta
    with freeze_time("2026-11-01 12:00:00"):
        headers = auth_header(user)

    with freeze_time("2026-11-01 12:14:00"):
        still_valid = await client.get("/auth/me", headers=headers)

    with freeze_time("2026-11-01 12:16:00"):
        expired = await client.get("/auth/me", headers=headers)


    assert still_valid.status_code == 200
    assert expired.status_code == 401
    assert expired.json()["code"] == "token_expired"




async def test_register_duplicate_username_is_409(client, session):
    await make_user(session, "ana@test.hr")

    response = await client.post(
        "/auth/register",
        json={"username": "ana@test.hr", "password": PASSWORD, "full_name": "Ana"},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "duplicate"
