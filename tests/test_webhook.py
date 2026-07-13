import pytest
from tests.conftest import make_webhook_signature


async def test_webhook_payment_success(client):
    payload = {
        "transaction_id": "test-tx-001",
        "user_id": 1,
        "account_id": 1,
        "amount": 100,
    }
    payload["signature"] = make_webhook_signature(payload)

    _, response = await client.post(
        "/api/v1/webhook/payment",
        json=payload,
    )
    assert response.status == 200
    data = response.json
    assert data["status"] == "success"
    assert data["transaction_id"] == "test-tx-001"
    assert data["account_id"] == 1
    assert data["amount"] == 100
    assert "balance" in data


async def test_webhook_creates_new_account(client):
    payload = {
        "transaction_id": "test-tx-new-acct",
        "user_id": 1,
        "account_id": 999,
        "amount": 50,
    }
    payload["signature"] = make_webhook_signature(payload)

    _, response = await client.post(
        "/api/v1/webhook/payment",
        json=payload,
    )
    assert response.status == 200
    data = response.json
    assert data["account_id"] == 999
    assert float(data["balance"]) == 50.0


async def test_webhook_duplicate_transaction(client):
    payload = {
        "transaction_id": "test-tx-dup",
        "user_id": 1,
        "account_id": 1,
        "amount": 10,
    }
    payload["signature"] = make_webhook_signature(payload)

    _, response = await client.post(
        "/api/v1/webhook/payment",
        json=payload,
    )
    assert response.status == 200

    _, response = await client.post(
        "/api/v1/webhook/payment",
        json=payload,
    )
    assert response.status == 409


async def test_webhook_invalid_signature(client):
    payload = {
        "transaction_id": "test-tx-bad-sig",
        "user_id": 1,
        "account_id": 1,
        "amount": 100,
        "signature": "0" * 64,
    }

    _, response = await client.post(
        "/api/v1/webhook/payment",
        json=payload,
    )
    assert response.status == 400


async def test_webhook_amount_zero(client):
    payload = {
        "transaction_id": "test-tx-zero",
        "user_id": 1,
        "account_id": 1,
        "amount": 0,
        "signature": "fake",
    }

    _, response = await client.post(
        "/api/v1/webhook/payment",
        json=payload,
    )
    assert response.status == 400


async def test_webhook_amount_negative(client):
    payload = {
        "transaction_id": "test-tx-neg",
        "user_id": 1,
        "account_id": 1,
        "amount": -10,
        "signature": "fake",
    }

    _, response = await client.post(
        "/api/v1/webhook/payment",
        json=payload,
    )
    assert response.status == 400


async def test_webhook_empty_body(client):
    _, response = await client.post(
        "/api/v1/webhook/payment",
        json={},
    )
    assert response.status == 400


async def test_webhook_missing_fields(client):
    _, response = await client.post(
        "/api/v1/webhook/payment",
        json={"transaction_id": "x"},
    )
    assert response.status == 400
