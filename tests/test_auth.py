import pytest


async def test_login_success(client):
    _, response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "user123"},
    )
    assert response.status == 200
    data = response.json
    assert "token" in data
    assert data["user"]["email"] == "user@example.com"
    assert data["user"]["full_name"] == "Test User"
    assert data["user"]["is_admin"] is False


async def test_login_admin(client):
    _, response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert response.status == 200
    data = response.json
    assert data["user"]["is_admin"] is True


async def test_login_wrong_password(client):
    _, response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "wrong"},
    )
    assert response.status == 401
    assert "error" in response.json


async def test_login_wrong_email(client):
    _, response = await client.post(
        "/api/v1/auth/login",
        json={"email": "noexist@test.com", "password": "user123"},
    )
    assert response.status == 401
    assert "error" in response.json


async def test_login_empty_body(client):
    _, response = await client.post(
        "/api/v1/auth/login",
        json={},
    )
    assert response.status == 400


async def test_login_no_body(client):
    _, response = await client.post("/api/v1/auth/login")
    assert response.status == 400


async def test_login_missing_fields(client):
    _, response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com"},
    )
    assert response.status == 400
