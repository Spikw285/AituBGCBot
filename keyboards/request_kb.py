from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Соглашение по callback_data: "<Module>:<Action>:<Value>"
# Пример: "game_req:game:3" - модуль game_req, действие game, id=3
# Позволяет router.py четко различать кнопки разных модулей

def games_keyboard(games: list[dict]) ->InlineKeyboardMarkup:
    """
    Генерирует inline-клавиатуру со списком игр
    :arg games: [{"id": 1, "title": "Catan"}, ...]
    """
    builder = InlineKeyboardBuilder()

    for game in games:
        builder.button(
            text=game["title"],
            callback_data=f"game_req:game:{game['id']}"
        )

    builder.button(text="Отмена", callback_data="game_req:cancel")
    builder.adjust(1) # По одной кнопке в ряд
    return builder.as_markup()

def gm_need_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа запроса к ГМу"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Порекомендуй игру", callback_data="gm_req:need:recommend")
    builder.button(text="Объясни правила", callback_data="gm_req:need:rules")
    builder.button(text="Отмена", callback_data="gm_req:cancel")
    builder.adjust(1)
    return builder.as_markup()

def games_for_gm_keyboard(games: list[dict]) -> InlineKeyboardMarkup:
    """Клавиатура выбора игры для запроса 'Объясни правила'. """
    builder = InlineKeyboardBuilder()

    for game in games:
        builder.button(
            text=game["title"],
            callback_data=f"gm_req:game:{game['id']}"
        )

    builder.button(text="Отмена", callback_data="gm_req:cancel")
    builder.adjust(1)
    return builder.as_markup()

def ttrpg_sessions_keyboard(sessions: list[dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора НРИ сессии
    :arg sessions: [{"id": 1, "title": "Curse of Strahd", "system" "DnD 5e", "type": "campaign"}, ...]
    """
    builder = InlineKeyboardBuilder()

    for session in sessions:
        icon = "📖" if session["type"] == "campaign" else "⚡"
        label = f"{icon} {session['title']} ({session['system']})"
        builder.button(
            text=label,
            callback_data=f"ttrpg:session:{session['id']}"
        )

    builder.button(text="Отмена", callback_data="ttrpg:cancel")
    builder.adjust(1)
    return builder.as_markup()

def confirm_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """
    Универсальная клавиатура подтверждения
    :arg prefix: "game_req" | "gm_req" | "ttrpg"
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить", callback_data=f"{prefix}:confirm")
    builder.button(text="Отменить", callback_data=f"{prefix}:cancel")
    builder.adjust(2) # Обе кнопки в одном ряду
    return builder.as_markup()

def skip_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'Пропустить' для опциональных шагов"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Пропустить", callback_data=f"{prefix}:skip")
    builder.button(text="Отмена", callback_data=f"{prefix}:cancel")
    builder.adjust(2)
    return builder.as_markup()