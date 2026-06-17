"""
Флоу: Запись на НРИ-сессию
============================
Участник выбирает открытый ваншот или кампанию и подаёт заявку.
DM получает уведомление (TODO: кнопки Принять/Отклонить — следующий этап).

  /ttrpg_signup
      -> [список открытых сессий]
      -> выбор сессии + детали
      -> комментарий о себе (или Пропустить)
      -> сводка + подтверждение
      -> сохранение в БД + уведомление DM
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import logging

from keyboards.request_kb import confirm_keyboard, skip_keyboard, ttrpg_sessions_keyboard
from states.request_states import TTRPGSignupFSM

log = logging.getLogger(__name__)

router = Router(name="ttrpg_signup")

# Метки типов сессий для отображения пользователю
SESSION_TYPE_LABELS: dict[str, str] = {
    "campaign": "Кампания",
    "oneshot":  "Ваншот",
}


@router.message(Command("ttrpg_signup"))
async def cmd_ttrpg_signup(message: Message, state: FSMContext) -> None:
    log.info("tg_id=%d started /ttrpg_signup", message.from_user.id)
    # TODO: заменить на запрос к БД
    # sessions = await get_open_sessions(db_session)
    mock_sessions = [
        {"id": 1, "title": "Curse of Strahd",  "system": "D&D 5e",      "type": "campaign"},
        {"id": 2, "title": "The Frozen Wastes", "system": "PF2e",        "type": "oneshot"},
        {"id": 3, "title": "Starfall",          "system": "Daggerheart", "type": "oneshot"},
    ]

    if not mock_sessions:
        log.info("tg_id=%d: no open ttrpg sessions available", message.from_user.id)
        await message.answer("Сейчас нет открытых НРИ-сессий. Следи за анонсами!")
        return

    await message.answer(
        "<b>Запись на НРИ</b>\n\nВыбери сессию:",
        reply_markup=ttrpg_sessions_keyboard(mock_sessions),
        parse_mode="HTML",
    )
    await state.set_state(TTRPGSignupFSM.choosing_session)


@router.callback_query(TTRPGSignupFSM.choosing_session, F.data.startswith("ttrpg:session:"))
async def on_session_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    session_id = int(callback.data.split(":")[-1])

    log.debug("tg_id=%d chose session_id=%d", callback.from_user.id, session_id)
    # TODO: получить детали сессии из БД
    # session = await get_session_by_id(db_session, session_id)
    mock_session = {
        "id":          session_id,
        "title":       f"Сессия #{session_id}",
        "system":      "D&D 5e",
        "type":        "campaign",
        "dm_name":     "Alex",
        "max_players": 5,
        "description": "Тёмное фэнтези, хоррор элементы.",
    }

    type_label = SESSION_TYPE_LABELS.get(mock_session["type"], mock_session["type"])

    # Сохраняем только то, что понадобится на следующих шагах
    await state.update_data(
        session_id    = session_id,
        session_title = mock_session["title"],
        dm_name       = mock_session["dm_name"],
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"<b>{mock_session['title']}</b>\n\n"
        f"Система: {mock_session['system']}\n"
        f"Тип: {type_label}\n"
        f"DM: {mock_session['dm_name']}\n"
        f"Мест: до {mock_session['max_players']}\n\n"
        f"{mock_session['description']}\n\n"
        "Расскажи немного о себе для DM-а:\n"
        "<i>Опыт в НРИ, пожелания по персонажу и т.п.</i>",
        reply_markup=skip_keyboard("ttrpg"),
        parse_mode="HTML",
    )
    await state.set_state(TTRPGSignupFSM.entering_comment)
    await callback.answer()


@router.message(TTRPGSignupFSM.entering_comment)
async def on_signup_comment_entered(message: Message, state: FSMContext) -> None:
    log.debug("tg_id=%d entered ttrpg comment", message.from_user.id)
    await state.update_data(comment=message.text.strip())
    await _show_ttrpg_summary(message, state)


@router.callback_query(TTRPGSignupFSM.entering_comment, F.data == "ttrpg:skip")
async def on_signup_comment_skipped(callback: CallbackQuery, state: FSMContext) -> None:
    log.debug("tg_id=%d skipped ttrpg comment", callback.from_user.id)
    await state.update_data(comment=None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await _show_ttrpg_summary(callback.message, state)
    await callback.answer()


async def _show_ttrpg_summary(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    comment_line = f"\nО себе: {data['comment']}" if data.get("comment") else ""

    await message.answer(
        "<b>Проверь заявку:</b>\n\n"
        f"Сессия: <b>{data['session_title']}</b>\n"
        f"DM: {data['dm_name']}"
        f"{comment_line}\n\n"
        "Подать заявку?",
        reply_markup=confirm_keyboard("ttrpg"),
        parse_mode="HTML",
    )
    await state.set_state(TTRPGSignupFSM.confirming)


@router.callback_query(TTRPGSignupFSM.confirming, F.data == "ttrpg:confirm")
async def on_signup_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    log.info(
        "tg_id=%d confirmed ttrpg_signup: session_id=%s, dm=%r",
        callback.from_user.id, data.get("session_id"), data.get("dm_name"),
    )

    # TODO: сохранить заявку в БД
    # await create_ttrpg_signup(
    #     db_session,
    #     member_tg_id = callback.from_user.id,
    #     session_id   = data["session_id"],
    #     comment      = data.get("comment"),
    # )

    # TODO: уведомить DM-а с кнопками Принять/Отклонить
    # dm_tg_id = await get_dm_telegram_id(db_session, data["session_id"])
    # await callback.bot.send_message(dm_tg_id, ..., reply_markup=dm_response_keyboard(...))

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Заявка на «{data['session_title']}» отправлена!\n"
        "DM рассмотрит её и скоро ответит."
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "ttrpg:cancel")
async def on_signup_cancelled(callback: CallbackQuery, state: FSMContext) -> None:
    log.info("tg_id=%d cancelled ttrpg_signup", callback.from_user.id)
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Запись отменена.")
    await callback.answer()