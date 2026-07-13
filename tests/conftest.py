import os
import tempfile
import pytest
import pytest_asyncio
from hashlib import sha256

import app.database as db_module
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models import Base, User, Account, Payment
from app.auth import hash_password, create_access_token
from app.config import Config
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp

from sanic import Sanic
from sanic_testing import TestManager
from sanic_ext import Extend


test_engine = None
test_session_factory = None


def _init_engine():
    global test_engine, test_session_factory
    if test_engine is None:
        path = os.path.join(tempfile.mkdtemp(), "test.db")
        url = f"sqlite+aiosqlite:///{path}"
        test_engine = create_async_engine(
            url, echo=False, connect_args={"check_same_thread": False}
        )
        test_session_factory = async_sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )
        db_module.engine = test_engine
        db_module.async_session_factory = test_session_factory
    return test_engine, test_session_factory


Sanic.test_mode = True
test_app = Sanic("TestDimatechAPI")
test_app.config.update({"DEBUG": False})

Extend(test_app)

test_app.ext.openapi.describe(title="Dimatech API Test", version="1.0.0")

test_app.blueprint(auth_bp)
test_app.blueprint(users_bp)
test_app.blueprint(admin_bp)
test_app.blueprint(webhook_bp)

TestManager(test_app)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    engine, factory = _init_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with factory() as session:
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

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    asgi_client = test_app._test_manager.asgi_client
    yield asgi_client


@pytest.fixture
def user_token():
    return create_access_token(1, False)


@pytest.fixture
def admin_token():
    return create_access_token(2, True)


def make_webhook_signature(data: dict) -> str:
    secret = Config.WEBHOOK_SECRET
    keys = sorted(k for k in data if k != "signature")
    concatenated = "".join(str(data[k]) for k in keys) + secret
    return sha256(concatenated.encode()).hexdigest()
