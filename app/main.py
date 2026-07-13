from sanic import Sanic
from sanic_ext import Extend

from app.config import Config
from app.database import engine, get_db_session
from app.models import Base, User, Account
from app.auth import hash_password
from sqlalchemy import select

app = Sanic("DimatechAPI")

app.config.update(
    {
        "DEBUG": Config.DEBUG,
    }
)

Extend(app)

app.ext.openapi.describe(
    title="Dimatech API",
    version="1.0.0",
    description="Асинхронное REST API для управления счетами и платежами",
)

from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp

app.blueprint(auth_bp)
app.blueprint(users_bp)
app.blueprint(admin_bp)
app.blueprint(webhook_bp)


async def seed_data():
    async with get_db_session() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        user = User(
            email="user@example.com",
            password_hash=hash_password("user123"),
            full_name="Test User",
            is_admin=False,
        )
        session.add(user)
        await session.flush()

        admin = User(
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            full_name="Test Admin",
            is_admin=True,
        )
        session.add(admin)
        await session.flush()

        account = Account(user_id=user.id, balance=1000)
        session.add(account)
        await session.commit()


@app.before_server_start
async def setup_db(app, loop):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_data()


@app.after_server_stop
async def close_db(app, loop):
    await engine.dispose()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=Config.DEBUG)
