"""
Запрос к ГМу (Гейм мастру)

/gm_request

Два пути в зависимости от need_type:
    recommend -> choosing_need -> entering_notes -> confirming
    rules     -> choosing_need -> choosing_game -> entering_notes -> confirming
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import logging

from keyboards.request_kb import (
    confirm_keyboard,
    games_for_gm_keyboard,
    gm_need_keyboard,
    skip_keyboard
)
from states.request_states import GMRequestFSM

log = logging.getLogger(__name__)

router = Router(name="gm_request")

# Константы типов запроса
NEED_RECOMMEND = "recommend"
NEED_RULES     = "rules"

# Step 1: Точка старта

@router.message(Command("gm_request"))
async def cmd_gm_request(message: Message, state: FSMContext) -> None:
    log.info("tg_id=%d started /gm_request", message.from_user.id)
    await message.answer(
        "<b>Запрос к Гейм Мастеру</b>\n\nЧем тебе может помочь ГМ?",
        reply_markup=gm_need_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(GMRequestFSM.choosing_need)

@router.callback_query(GMRequestFSM.choosing_need, F.data.startswith("gm_req:need:"))
async def on_need_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """
    callback.data: "gm_req:need:recommend" или "gm_req:need:rules"

    Парсит последний сегмент для определения пути
    """
    need_type = callback.data.split(":")[-1]

    log.debug("tg_id=%d chose need_type=%r", callback.from_user.id, need_type)
    await state.update_data(need_type=need_type, game_id=None, game_title=None)
    await callback.message.edit_reply_markup(reply_markup=None)

    if need_type == NEED_RECOMMEND:
        # Если нужна рекомендация, берём игры с БД
        # TODO: заменить на запрос к БД
        mock_games = [
            {"id": 1, "title": "Catan"},
            {"id": 2, "title": "Res Arcana"},
        ]

        await callback.message.answer(
            "Для какой игры нужна помощь с правилами?",
            reply_markup=games_for_gm_keyboard(mock_games),
        )
        await state.set_state(GMRequestFSM.choosing_game)
    else:
        # Если нужна рекомендация, игра не нужна - сразу к заметкам
        await _ask_for_notes(callback.message, state)

    await callback.answer()

# Step 2: Пользователю нужно объяснить правила для игры

@router.callback_query(GMRequestFSM.choosing_game, F.data.startswith("gm_req:game:"))
async def on_game_for_rules_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    game_id = int(callback.data.split(":")[-1])

    # TODO: получить из БД
    game_title = f"Игра #{game_id}"

    log.debug("tg_id=%d chose game_id=%d for rules (%s)", callback.from_user.id, game_id, game_title)
    await state.update_data(game_id=game_id, game_title=game_title)
    await callback.message.edit_reply_markup(reply_markup=None)
    await _ask_for_notes(callback.message, state)
    await callback.answer()

async def _ask_for_notes(message: Message, state: FSMContext) -> None:
    """Вспомогательная функция, позволяющая оставлять заметки"""
    await message.answer(
        "Есть что добавить для ГМа? (необязательно)\n"
        "<i>Например: «Нас 5 человек, опыт минимальный»</i>",
        reply_markup=skip_keyboard("gm_req"),
        parse_mode="HTML",
    )
    await state.set_state(GMRequestFSM.entering_notes)

# Step 3: Пользователь пишет заметку (независимо от того, как он сюда попал)

@router.message(GMRequestFSM.entering_notes)
async def on_notes_entered(message: Message, state: FSMContext) -> None:
    log.debug("tg_id=%d entered notes", message.from_user.id)
    await state.update_data(notes=message.text.strip())
    await _show_gm_request_summary(message, state)

@router.callback_query(GMRequestFSM.entering_notes, F.data == "gm_req:skip")
async def on_notes_skipped(callback: CallbackQuery, state: FSMContext) -> None:
    log.debug("tg_id=%d skipped notes", callback.from_user.id)
    await state.update_data(notes=None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await _show_gm_request_summary(callback.message, state)
    await callback.answer()

async def _show_gm_request_summary(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    need_label = "Порекомендуй игру" if data["need_type"] == NEED_RECOMMEND else "Объясни правила"
    game_line  = f"\nИгра: <b>{data['game_title']}</b>" if data.get("game_title") else ""
    notes_line = f"\nЗаметки: {data['notes']}" if data.get("notes") else ""

    await message.answer(
        "<b>Проверь запрос:</b>\n\n"
        f"Тип: {need_label}\n"
        f"{game_line}"
        f"{notes_line}\n\n"
        "Отправить?",
        reply_markup=confirm_keyboard("gm_req"),
        parse_mode="HTML",
    )
    await state.set_state(GMRequestFSM.confirming)

# Step 4: Подтверждение пользователя на вызов ГМа

@router.callback_query(GMRequestFSM.confirming, F.data == "gm_req:confirm")
async def on_gm_request_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    log.info(
        "tg_id=%d confirmed gm_request: need_type=%r, game_id=%s",
        callback.from_user.id, data.get("need_type"), data.get("game_id"),
    )

    # TODO: сохранить в БД и уведомить ГМов

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Запрос к ГМу отправлен!")
    await state.clear()
    await callback.answer()


# Возможность отменить запрос в любое время
@router.callback_query(F.data == "gm_req:cancel")
async def on_gm_request_cancelled(callback:CallbackQuery, state:FSMContext) -> None:
    log.info("tg_id=%d cancelled gm_request", callback.from_user.id)
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Запрос отменён")
    await callback.answer()