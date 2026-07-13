import pytest


async def test_get_me(client, user_token):
    _, response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 200
    data = response.json
    assert data["email"] == "user@example.com"
    assert data["full_name"] == "Test User"
    assert data["is_admin"] is False
    assert "id" in data
    assert "created_at" in data


async def test_get_me_unauthorized(client):
    _, response = await client.get("/api/v1/users/me")
    assert response.status == 401
    assert "error" in response.json


async def test_get_me_invalid_token(client):
    _, response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status == 401


async def test_get_my_accounts(client, user_token):
    _, response = await client.get(
        "/api/v1/users/me/accounts",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) >= 1
    account = data[0]
    assert account["user_id"] == 1
    assert account["balance"] == 1000.0
    assert "id" in account
    assert "created_at" in account


async def test_get_my_accounts_unauthorized(client):
    _, response = await client.get("/api/v1/users/me/accounts")
    assert response.status == 401


async def test_get_my_payments(client, user_token):
    _, response = await client.get(
        "/api/v1/users/me/payments",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 200
    data = response.json
    assert isinstance(data, list)


async def test_get_my_payments_unauthorized(client):
    _, response = await client.get("/api/v1/users/me/payments")
    assert response.status == 401
