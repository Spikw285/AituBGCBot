from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


# Движок — одно соединение с БД на всё приложение.
# pool_size     — сколько соединений держать открытыми постоянно
# max_overflow  — сколько дополнительных соединений можно открыть в пике
# echo=False    — не печатать каждый SQL-запрос в консоль (поставь True для дебага)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

# Фабрика сессий.
# expire_on_commit=False — объекты остаются читаемыми после commit(),
# что важно в async контексте
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Базовый класс для всех SQLAlchemy-моделей проекта.
    Все модели наследуются от него — это нужно Alembic
    чтобы найти таблицы при генерации миграций.

    Пример:
        class GameRequest(Base):
            __tablename__ = "game_requests"
            ...
    """
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async-генератор сессии для прямого использования вне middleware.
    Автоматически закрывает сессию после выхода из блока async with.

    Пример использования:
        async with get_session() as session:
            result = await session.execute(...)
    """
    async with AsyncSessionFactory() as session:
        yield session