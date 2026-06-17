from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Все конфиги берутся из .env файла автоматически.
    pydantic-settings сам читает файл и валидирует типы.

    Пример .env:
        BOT_TOKEN=1234567890:AAF...
        DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Telegram
    BOT_TOKEN: str

    # PostgreSQL — asyncpg драйвер (async-совместимый)
    DATABASE_URL: str

    DEBUG: bool = False

# Единственный экземпляр на всё приложение.
# Импортируем отовсюду: from config import settings
settings = Settings()