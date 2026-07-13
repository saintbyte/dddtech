import pytest


async def test_list_users(client, admin_token):
    _, response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 2
    emails = [u["email"] for u in data]
    assert "user@example.com" in emails
    assert "admin@example.com" in emails


async def test_list_users_not_admin(client, user_token):
    _, response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 403


async def test_list_users_unauthorized(client):
    _, response = await client.get("/api/v1/admin/users")
    assert response.status == 401


async def test_create_user(client, admin_token):
    _, response = await client.post(
        "/api/v1/admin/users",
        json={
            "email": "new@test.com",
            "password": "pass123",
            "full_name": "New User",
            "is_admin": False,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 201
    data = response.json
    assert data["email"] == "new@test.com"
    assert data["full_name"] == "New User"
    assert data["is_admin"] is False
    assert "id" in data
    assert "created_at" in data


async def test_create_user_duplicate_email(client, admin_token):
    _, response = await client.post(
        "/api/v1/admin/users",
        json={
            "email": "user@example.com",
            "password": "pass123",
            "full_name": "Dup",
            "is_admin": False,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 409


async def test_create_user_validation_error(client, admin_token):
    _, response = await client.post(
        "/api/v1/admin/users",
        json={"email": "bad"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 400


async def test_create_user_not_admin(client, user_token):
    _, response = await client.post(
        "/api/v1/admin/users",
        json={
            "email": "x@test.com",
            "password": "pass",
            "full_name": "X",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 403


async def test_update_user(client, admin_token):
    _, response = await client.put(
        "/api/v1/admin/users/1",
        json={"full_name": "Updated User"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 200
    data = response.json
    assert data["full_name"] == "Updated User"
    assert data["email"] == "user@example.com"


async def test_update_user_password(client, admin_token):
    _, response = await client.put(
        "/api/v1/admin/users/1",
        json={"password": "newpass"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 200


async def test_update_user_not_found(client, admin_token):
    _, response = await client.put(
        "/api/v1/admin/users/999",
        json={"full_name": "X"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 404


async def test_update_user_not_admin(client, user_token):
    _, response = await client.put(
        "/api/v1/admin/users/1",
        json={"full_name": "X"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 403


async def test_delete_user(client, admin_token):
    _, response = await client.post(
        "/api/v1/admin/users",
        json={
            "email": "del@test.com",
            "password": "pass",
            "full_name": "Del Me",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 201
    user_id = response.json["id"]

    _, response = await client.delete(
        f"/api/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 200
    assert response.json["message"] == "User deleted"


async def test_delete_user_not_found(client, admin_token):
    _, response = await client.delete(
        "/api/v1/admin/users/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 404


async def test_delete_user_not_admin(client, user_token):
    _, response = await client.delete(
        "/api/v1/admin/users/1",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 403


async def test_get_user_accounts(client, admin_token):
    _, response = await client.get(
        "/api/v1/admin/users/1/accounts",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["user_id"] == 1


async def test_get_user_accounts_not_found(client, admin_token):
    _, response = await client.get(
        "/api/v1/admin/users/999/accounts",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status == 404


async def test_get_user_accounts_not_admin(client, user_token):
    _, response = await client.get(
        "/api/v1/admin/users/1/accounts",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status == 403
