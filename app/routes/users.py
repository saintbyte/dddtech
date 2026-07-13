from sanic import Blueprint
from sanic.request import Request
from sanic_ext.extensions.openapi import openapi
from sqlalchemy import select

from app.database import get_db_session
from app.decorators import require_auth
from app.models import Account, Payment
from app.response import response_result
from app.schemas import AccountResponse, PaymentResponse, UserResponse

users_bp = Blueprint("users", url_prefix="/api/v1/users")


@openapi.definition(
    summary="Профиль текущего пользователя",
    description="Возвращает профиль текущего аутентифицированного пользователя",
    response={
        200: openapi.response(200, "Профиль пользователя", UserResponse),
        401: openapi.response(401, "Не авторизован"),
    },
    tag="Users",
)
@users_bp.get("/me")
@require_auth
async def get_me(request: Request):
    user = request.ctx.user
    return response_result(UserResponse, user)


@openapi.definition(
    summary="Мои счета",
    description="Возвращает список счетов текущего аутентифицированного пользователя",
    response={
        200: openapi.response(200, "Список счетов", [AccountResponse]),
        401: openapi.response(401, "Не авторизован"),
    },
    tag="Users",
)
@users_bp.get("/me/accounts")
@require_auth
async def get_my_accounts(request: Request):
    user = request.ctx.user
    async with get_db_session() as session:
        result = await session.execute(
            select(Account).where(Account.user_id == user.id)
        )
        accounts = result.scalars().all()
        return response_result(AccountResponse, accounts)


@openapi.definition(
    summary="Мои платежи",
    description="Возвращает список платежей текущего аутентифицированного пользователя",
    response={
        200: openapi.response(200, "Список платежей", [PaymentResponse]),
        401: openapi.response(401, "Не авторизован"),
    },
    tag="Users",
)
@users_bp.get("/me/payments")
@require_auth
async def get_my_payments(request: Request):
    user = request.ctx.user
    async with get_db_session() as session:
        result = await session.execute(
            select(Payment).where(Payment.user_id == user.id)
        )
        payments = result.scalars().all()
        return response_result(PaymentResponse, payments)
