from sanic import Blueprint, json
from sanic.request import Request
from sanic_ext.extensions.openapi import openapi
from pydantic import ValidationError
from sqlalchemy import select

from app.auth import hash_password
from app.database import get_db_session
from app.decorators import require_admin
from app.models import User, Account
from app.response import response_error, response_message, response_result
from app.schemas import AccountResponse, UserCreateRequest, UserUpdateRequest, UserResponse

admin_bp = Blueprint("admin", url_prefix="/api/v1/admin")


@openapi.definition(
    summary="Список всех пользователей",
    description="Возвращает список всех зарегистрированных пользователей. Требуются права администратора.",
    response={
        200: openapi.response(200, "Список пользователей", [UserResponse]),
        401: openapi.response(401, "Не авторизован"),
        403: openapi.response(403, "Требуются права администратора"),
    },
    tag="Admin",
)
@admin_bp.get("/users")
@require_admin
async def list_users(request: Request):
    async with get_db_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return response_result(UserResponse, users)


@openapi.definition(
    summary="Создание пользователя",
    description="Создаёт новый аккаунт пользователя. Требуются права администратора.",
    body={"application/json": UserCreateRequest},
    response={
        201: openapi.response(201, "Пользователь создан", UserResponse),
        400: openapi.response(400, "Ошибка валидации"),
        401: openapi.response(401, "Не авторизован"),
        409: openapi.response(409, "Пользователь с таким email уже существует"),
        403: openapi.response(403, "Требуются права администратора"),
    },
    tag="Admin",
)
@admin_bp.post("/users")
@require_admin
async def create_user(request: Request):
    raw = request.json
    if not raw:
        return response_error("Request body is required", 400)

    try:
        data = UserCreateRequest.model_validate(raw)
    except ValidationError as e:
        return response_error("Validation failed", 400, details=e.errors(include_input=False))

    async with get_db_session() as session:
        existing = await session.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            return response_error("User with this email already exists", 409)

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            is_admin=data.is_admin,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return response_result(UserResponse, user, status=201)


@openapi.definition(
    summary="Обновление пользователя",
    description="Обновляет данные пользователя по ID. Требуются права администратора.",
    body={"application/json": UserUpdateRequest},
    response={
        200: openapi.response(200, "Пользователь обновлён", UserResponse),
        400: openapi.response(400, "Ошибка валидации"),
        401: openapi.response(401, "Не авторизован"),
        404: openapi.response(404, "Пользователь не найден"),
        403: openapi.response(403, "Требуются права администратора"),
    },
    tag="Admin",
)
@admin_bp.put("/users/<user_id:int>")
@require_admin
async def update_user(request: Request, user_id: int):
    raw = request.json
    if not raw:
        return response_error("Request body is required", 400)

    try:
        data = UserUpdateRequest.model_validate(raw)
    except ValidationError as e:
        return response_error("Validation failed", 400, details=e.errors(include_input=False))

    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return response_error("User not found", 404)

        if data.email is not None:
            user.email = data.email
        if data.password is not None:
            user.password_hash = hash_password(data.password)
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.is_admin is not None:
            user.is_admin = data.is_admin

        await session.commit()
        await session.refresh(user)
        return response_result(UserResponse, user)


@openapi.definition(
    summary="Удаление пользователя",
    description="Удаляет пользователя по ID. Требуются права администратора.",
    response={
        200: openapi.response(200, "Пользователь удалён"),
        401: openapi.response(401, "Не авторизован"),
        404: openapi.response(404, "Пользователь не найден"),
        403: openapi.response(403, "Требуются права администратора"),
    },
    tag="Admin",
)
@admin_bp.delete("/users/<user_id:int>")
@require_admin
async def delete_user(request: Request, user_id: int):
    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return response_error("User not found", 404)

        await session.delete(user)
        await session.commit()
        return response_message("User deleted")


@openapi.definition(
    summary="Счета пользователя",
    description="Возвращает список счетов указанного пользователя. Требуются права администратора.",
    response={
        200: openapi.response(200, "Список счетов", [AccountResponse]),
        401: openapi.response(401, "Не авторизован"),
        404: openapi.response(404, "Пользователь не найден"),
        403: openapi.response(403, "Требуются права администратора"),
    },
    tag="Admin",
)
@admin_bp.get("/users/<user_id:int>/accounts")
@require_admin
async def get_user_accounts(request: Request, user_id: int):
    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return response_error("User not found", 404)

        accounts_result = await session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        accounts = accounts_result.scalars().all()
        return response_result(AccountResponse, accounts)
