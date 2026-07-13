from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import Config

engine = create_async_engine(Config.DATABASE_URL, echo=Config.DEBUG)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_db_session() -> AsyncSession:
    return async_session_factory()
