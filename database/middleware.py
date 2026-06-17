from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.base import AsyncSessionFactory


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware создаёт сессию БД для каждого входящего апдейта
    и кладёт её в data["session"].

    После этого любой хендлер может получить сессию просто добавив
    параметр session: AsyncSession в сигнатуру функции.

    Пример хендлера с сессией:
        @router.message(Command("start"))
        async def cmd_start(message: Message, session: AsyncSession) -> None:
            result = await session.execute(select(Member))
            ...

    Сессия автоматически закрывается после обработки апдейта.
    При исключении — rollback происходит автоматически через контекст-менеджер.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with AsyncSessionFactory() as session:
            data["session"] = session  # хендлеры получают сессию отсюда
            return await handler(event, data)