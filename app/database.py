from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from typing import AsyncGenerator

from app.config import settings

engine = create_async_engine(url=settings.postgre_dsn, echo=True)
AsyncSessionFactory = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию для работы с БД"""

    async with AsyncSessionFactory() as async_session:
        yield async_session
