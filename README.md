# 🎲 AITU Board Games Club Bot

Telegram-бот для управления клубом настольных игр AITU.  
Инвентарь, выдача игр, запросы к GM, НРИ-кампании — всё в одном месте.

---

## Модули

| Модуль | Что делает | Ответственный |
|--------|-----------|---------------|
| **Core** | Регистрация, роли, уровни доверия, уведомления | @SodaPowder   |
| **Boardgame** | Инвентарь, выдача/возврат игр, логи | @kasapwy      |
| **Requests** | Запросы на игру, запросы к GM, запись на НРИ | @CallMeKasym  |

---

## Стек

- **Python 3.12**
- **aiogram 3.x** — Telegram Bot Framework
- **SQLAlchemy 2.x (async)** — ORM
- **asyncpg** — async PostgreSQL драйвер
- **Alembic** — миграции БД
- **PostgreSQL** (Neon) — база данных
- **pydantic-settings** — конфигурация через `.env`
- **APScheduler** — напоминания о просрочках

---

## Быстрый старт

### 1. Клонировать репо

```bash
git clone https://github.com/<org>/club-bot.git
cd AituBGCBot
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -e ".[dev]"
```

### 4. Настроить переменные окружения

```bash
cp .env.example .env
# открыть .env и заполнить BOT_TOKEN и DATABASE_URL
```

### 5. Применить миграции

```bash
alembic upgrade head
```

### 6. Запустить бота

```bash
python main.py
```

---

## Структура проекта

```
club_bot/
├── main.py                  # точка входа
├── config.py                # настройки из .env
│
├── database/
│   ├── base.py              # движок, сессия, Base
│   ├── middleware.py        # пробрасывает сессию в хендлеры
│   └── models/
│       ├── member.py        # Member, MemberRole, TrustLevelRef
│       ├── game.py          # Game, GameCopy
│       ├── borrow_log.py    # BorrowLog
│       ├── request.py       # GameRequest, GMRequest
│       └── ttrpg.py         # Campaign, Session, TTRPGSignup и др.
│
├── handlers/
│   ├── common.py            # /start, /help
│   ├── inventory/           # просмотр и управление инвентарём
│   ├── borrow/              # выдача и возврат игр
│   └── requests/            # запросы участников
│
├── services/                # бизнес-логика (без Telegram)
├── states/                  # FSM состояния
├── keyboards/               # inline клавиатуры
└── migrations/              # Alembic миграции
```

---

## Разработка

### Ветки

```
main          стабильная (только через PR)
dev           основная ветка разработки
feature/<name>  для каждой фичи
```

### Соглашение по коммитам

```
feat:     новая функциональность
fix:      исправление бага
refactor: рефакторинг без изменения логики
docs:     документация
test:     тесты
chore:    служебное (зависимости, конфиги)
```

### Правила PR

- Минимум **1 ревью** перед мёржем в `dev`
- Тесты не падают
- Описание PR: что сделано + как проверить

---

## Переменные окружения

Скопировать `.env.example` → `.env` и заполнить:

```env
BOT_TOKEN=       # токен от @BotFather
DATABASE_URL=    # postgresql+asyncpg://user:pass@host/dbname
```

---

## База данных

Схема и описание всех таблиц — в [`docs/db_models.md`](docs/db_models.md).

Создать новую миграцию после изменения моделей:

```bash
alembic revision --autogenerate -m "описание изменения"
alembic upgrade head
```

---

## Статус разработки

> 🚧 Проект в активной разработке. Документация обновляется по мере готовности модулей.