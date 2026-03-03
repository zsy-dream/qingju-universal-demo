from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def _make_sqlite_async_url(path: str) -> str:
    # path expected like ./data/app.db
    # SQLAlchemy async SQLite URL
    clean = path.replace("\\", "/")
    return f"sqlite+aiosqlite:///{clean}".replace("////", "///")


engine = create_async_engine(
    _make_sqlite_async_url(settings.SQLITE_DB_PATH),
    future=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
