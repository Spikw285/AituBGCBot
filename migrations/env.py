import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# импортируем конфиг и base
from config import settings
from database.base import Base

# импорт моделей
# TODO: реализовать реальные импорты с реализациями

# from database.models.member import Member, MemberRole, TrustLevelRef
# IMPORTANT: при изменении имени модели строго прописать как оно называется, как реализовано

# from database.models.game import Game, GameCopy
# from database.models.borrow_log import BorrowLog
# IMPORTANT: при изменении имени модели строго прописать как оно называется, как реализовано

from database.models.request import GameRequest, GMRequest
from database.models.ttrpg import (
    DMProfile, DMProfileSystem, TTRPGSystem,
    Campaign, Session, TTRPGSignup,
)
# IMPORTANT: при изменении имени модели строго прописать как оно называется, как реализовано

# стандартная настройка Alembic

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Сравнение Base.metadata с реальной БД при -autogenerate
target_metadata = Base.metadata

# offline mode
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# online mode
def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # изменения типов колонок
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# точка входа

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
