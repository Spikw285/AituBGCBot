import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database.base import engine
from database.middleware import DatabaseMiddleware
from handlers.requests import router as requests_router

from logger import setup_logging, logging

async def main() -> None:
    setup_logging(debug=settings.DEBUG)
    log = logging.getLogger(__name__)


    bot = Bot(token=settings.BOT_TOKEN)

    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DatabaseMiddleware())
    dp.include_router(requests_router)

    try:
        log.info("Бот запущен...")
        await dp.start_polling(bot)
    finally:
        await engine.dispose()
        await bot.session.close()
        log.info("Бот остановлен.")

if __name__ == "__main__":
    asyncio.run(main())