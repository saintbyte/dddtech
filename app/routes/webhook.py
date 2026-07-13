from sanic import Blueprint
from sanic.request import Request
from sanic_ext.extensions.openapi import openapi
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db_session
from app.models import Account, Payment
from app.response import response_error, response_result
from app.schemas import PaymentWebhookResponse

from app.config import Config
from hashlib import sha256

webhook_bp = Blueprint("webhook", url_prefix="/api/v1/webhook")


class PaymentWebhook(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: float = Field(gt=0)
    signature: str

def _verify_webhook_signature(data: dict) -> bool:
    secret = Config.WEBHOOK_SECRET
    keys = sorted(k for k in data if k != "signature")
    concatenated = "".join(str(data[k]) for k in keys) + secret
    expected = sha256(concatenated.encode()).hexdigest()
    return expected == data.get("signature", "")

@openapi.definition(
    summary="Обработка вебхука платежа",
    description=(
        "Принимает входящий платёж и обновляет баланс счёта. "
        "Требуется корректная HMAC-SHA256 подпись."
    ),
    body={"application/json": PaymentWebhook},
    response={
        200: openapi.response(200, "Платёж успешно обработан", PaymentWebhookResponse),
        400: openapi.response(400, "Ошибка валидации или неверная подпись"),
        409: openapi.response(409, "Транзакция уже обработана"),
    },
    tag="Webhook",
)
@webhook_bp.post("/payment")
async def handle_payment_webhook(request: Request):
    raw = request.json
    if not raw:
        return response_error("Request body is required", 400)

    try:
        data = PaymentWebhook.model_validate(raw)
    except ValidationError as e:
        return response_error("Validation failed", 400, details=e.errors(include_input=False))

    if not _verify_webhook_signature(raw):
        return response_error("Invalid signature", 400)

    async with get_db_session() as session:
        existing = await session.execute(
            select(Payment).where(Payment.transaction_id == data.transaction_id)
        )
        if existing.scalar_one_or_none():
            return response_error("Transaction already processed", 409)

        account_result = await session.execute(
            select(Account).where(Account.id == data.account_id)
        )
        account = account_result.scalar_one_or_none()

        if not account:
            account = Account(id=data.account_id, user_id=data.user_id, balance=0)
            session.add(account)
            await session.flush()

        payment = Payment(
            transaction_id=data.transaction_id,
            account_id=account.id,
            user_id=data.user_id,
            amount=data.amount,
        )
        session.add(payment)

        account.balance = float(account.balance) + data.amount

        try:
            await session.commit()
            return response_result(PaymentWebhookResponse, {
                "status": "success",
                "transaction_id": data.transaction_id,
                "account_id": account.id,
                "amount": data.amount,
                "balance": str(account.balance),
            })
        except IntegrityError:
            await session.rollback()
            return response_error("Transaction already processed", 409)
