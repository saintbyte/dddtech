from sanic import Blueprint, json
from sanic.request import Request
from sanic_ext.extensions.openapi import openapi
from pydantic import ValidationError
from sqlalchemy import select

from app.auth import verify_password, create_access_token
from app.database import get_db_session
from app.models import User
from app.response import response_error
from app.schemas import LoginRequest, LoginResponse, UserResponse

auth_bp = Blueprint("auth", url_prefix="/api/v1/auth")


@openapi.definition(
    summary="Авторизация пользователя",
    description="Аутентификация по email и паролю для получения JWT-токена",
    body={"application/json": LoginRequest},
    response={
        200: openapi.response(200, "Успешная аутентификация", LoginResponse),
        400: openapi.response(400, "Ошибка валидации"),
        401: openapi.response(401, "Неверные учётные данные"),
    },
    tag="Auth",
)
@auth_bp.post("/login")
async def login(request: Request):
    raw = request.json
    if not raw:
        return response_error("Request body is required", 400)

    try:
        data = LoginRequest.model_validate(raw)
    except ValidationError as e:
        return response_error("Validation failed", 400, details=e.errors(include_input=False))

    async with get_db_session() as session:
        result = await session.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.password_hash):
            return response_error("Invalid email or password", 401)

        token = create_access_token(user.id, user.is_admin)
        return json(LoginResponse(token=token, user=UserResponse.model_validate(user)).model_dump(mode="json"))

