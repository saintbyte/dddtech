from functools import wraps

from sanic.request import Request
from sqlalchemy import select

from app.auth import decode_access_token
from app.database import get_db_session
from app.models import User
from app.response import response_error


def require_auth(handler):
    @wraps(handler)
    async def wrapper(request: Request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return response_error("Отсутствует или неверен заголовок авторизации", 401)

        try:
            token = auth_header[7:]
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
        except Exception:
            return response_error("Неверный или просроченный токен", 401)

        async with get_db_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

        if user is None:
            return response_error("Пользователь не найден", 401)

        request.ctx.user = user
        return await handler(request, *args, **kwargs)

    return wrapper


def require_admin(handler):
    @wraps(handler)
    async def wrapper(request: Request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return response_error("Отсутствует или неверен заголовок авторизации", 401)

        try:
            token = auth_header[7:]
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
        except Exception:
            return response_error("Неверный или просроченный токен", 401)

        async with get_db_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

        if user is None:
            return response_error("Пользователь не найден", 401)

        if not user.is_admin:
            return response_error("Требуются права администратора", 403)

        request.ctx.user = user
        return await handler(request, *args, **kwargs)

    return wrapper
