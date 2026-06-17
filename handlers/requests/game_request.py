"""
Запрос на конкретную игру

Участник хочет сыграть в конкретную настолку -> ГМ приносит её

Шаги:
    /game_request
        -> [inline список игр]
        -> выбор игры
        -> ввод желаемой игры
        -> комментарий (опционально)
        -> сводка + подтверждение
        -> сохранение в БД + уведомление ГМов
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import logging

from keyboards.request_kb import confirm_keyboard, games_keyboard, skip_keyboard
from states.request_states import GameRequestFSM

log = logging.getLogger(__name__)

router = Router(name="game_request")

# Step 1: точка начала

@router.message(Command("game_request"))
async def cmd_game_request(message: Message, state: FSMContext) -> None:
    """
    Точка входа. Срабатывает на команду /game_request

    state (FSMContext) — объект через который мы:
    - переключаем шаги:       await state.set_state(...)
    - сохраняем данные:       await state.update_data(key=value)
    - читаем сохранённые:     await state.get_data()
    - сбрасываем всё:         await state.clear()
    """
    # TODO: заменить mock на реальный запрос к БД
    # from services.request_service import get_available_games
    # games = await get_available_games(db_session)
    mock_games = [
        {"id": 1, "title": "Catan"},
        {"id": 2, "title": "Res Arcana"},
        {"id": 3, "title": "Bunker"},
    ]

    log.info("tg_id=%d started /game_request", message.from_user.id)

    if not mock_games:
        log.info("tg_id=%d: no games available", message.from_user.id)
        await message.answer("Сейчас нет доступных игр в инвентаре...")
        return

    await message.answer(
        "<b>Запрос на игру</b>\n\nВыбери игру из списка:",
        reply_markup=games_keyboard(mock_games),
        parse_mode="HTML",
    )

    # Переводим пользователя на первый шаг FSM
    # Теперь только хендлеры с фильтром GameRequestFSM.choosing_game
    # будут реагировать на сообщения этого пользователя
    await state.set_state(GameRequestFSM.choosing_game)

# Step 2: Пользователь выбрал игру

@router.callback_query(
        GameRequestFSM.choosing_game,       # Сработает только на этом шаге FSM
        F.data.startswith("game_req:game:"), # и только для этих callback_data
    )
async def on_game_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Пользователь нажал кнопку с игрой.
    callback.data имеет формат 'game_req:game:<id>', например 'game_req:game:3'
    """
    game_id = int(callback.data.split(":")[-1])

    # TODO: получить название из БД по game_id
    # game = await get_game_by_id(db_session, game_id)
    # game_title = game.title
    game_title = f"Игра #{game_id}" # заглушка

    log.debug("tg_id=%d chose game_id=%d (%s)", callback.from_user.id, game_id, game_title)
    await state.update_data(game_id=game_id, game_title=game_title)

    # Убираем кнопки у предыдущего сообщения
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        f"Выбрана: <b>{game_title}</b>\n\n"
        "В какое время хочешь играть?\n"
        "<i>Можно в свободной форме: «в эту пятницу» или «21 июня»</i>",
        parse_mode="HTML",
    )

    await state.set_state(GameRequestFSM.entering_date)
    await callback.answer() # Убирает "часы" на кнопке в телеграм

# Step 3: Пользователь ввёл дату

@router.message(GameRequestFSM.entering_date)
async def on_date_entered(message: Message, state: FSMContext) -> None:
    """Получаем желаемую дату. Принимаем свободный текст"""
    desired_date = message.text.strip()

    if len(desired_date) < 2:
        log.debug("tg_id=%d entered too-short date, prompting again", message.from_user.id)
        await message.answer("Пожалуйста, введи дату чуть подробнее.")
        return # остаёмся с тем же state

    log.debug("tg_id=%d entered date: %r", message.from_user.id, desired_date)
    await state.update_data(desired_date=desired_date)

    await message.answer(
        "Хочешь добавить комментарий для ГМа? (необязательно)\n"
        "<i>Например «Нас будет 4 человека» или «Первый раз играем»</i>",
        reply_markup=skip_keyboard("game_req"),
        parse_mode="HTML",
    )
    await state.set_state(GameRequestFSM.entering_comment)

# Step 4: Пользователь пишет комментарий

# Если пользователь написал комментарий
@router.message(GameRequestFSM.entering_comment)
async def on_comment_entered(message: Message, state: FSMContext) -> None:
    log.debug("tg_id=%d entered comment", message.from_user.id)
    await state.update_data(comment=message.text.strip())
    await _show_game_request_summary(message, state)

# Если пользователь пропустил
@router.callback_query(GameRequestFSM.entering_comment, F.data == "game_req:skip")
async def on_comment_skipped(callback: CallbackQuery, state: FSMContext) -> None:
    log.debug("tg_id=%d skipped comment", callback.from_user.id)
    await state.update_data(comment=None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await _show_game_request_summary(callback.message, state)
    await callback.answer()

async def _show_game_request_summary(message: Message, state: FSMContext) -> None:
    """Показывает итоговую сводку перед отправкой """
    data = await state.get_data()

    comment_line = f"\n Комментарий: {data['comment']}" if data.get('comment') else ""

    await message.answer(
        "<b>Проверь запрос перед отправкой:</b>\n\n"
        f"Игра: <b>{data['game_title']}</b>\n"
        f"Дата: {data['desired_date']}"
        f"{comment_line}\n\n"
        "Всё верно?",
        reply_markup=confirm_keyboard("game_req"),
        parse_mode="HTML",
    )

    await state.set_state(GameRequestFSM.confirming)

# Step 5: Подтверждение

@router.callback_query(GameRequestFSM.confirming, F.data == "game_req:confirm")
async def on_game_request_confirmed(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    log.info(
        "tg_id=%d confirmed game_request: game_id=%s, date=%r",
        callback.from_user.id, data.get("game_id"), data.get("desired_date"),
    )

    # TODO: сохранить запрос в БД
    # await create_game_request(
    #     db_session,
    #     member_tg_id = callback.from_user.id,
    #     game_id      = data["game_id"],
    #     desired_date = data["desired_date"],
    #     comment      = data.get("comment"),
    # )

    # TODO: уведомить ГМов
    # gm_ids = await get_gm_telegram_ids(db_session)
    # for gm_id in gm_ids:
    #     await callback.bot.send_message(
    #         chat_id=gm_id,
    #         text=(
    #             f"Новый запрос на игру!\n"
    #             f"От: {callback.from_user.full_name}\n"
    #             f"Игра: {data['game_title']}\n"
    #             f"Дата: {data['desired_date']}"
    #         ),
    #     )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Запрос отправлен! ГМ скоро свяжется с тобой.")

    # Очищаем state — пользователь полностью вышел из FSM
    await state.clear()
    await callback.answer()


# Отмена запроса (работает в любом шаге флоу)
@router.callback_query(F.data == "game_req:cancel")
async def on_game_request_cancelled(callback: CallbackQuery, state:FSMContext) -> None:
    """Функция работает без фильтра по state, т.е. сработает в любом из шагов"""
    log.info("tg_id=%d cancelled game_request", callback.from_user.id)
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Запрос отменён")
    await callback.answer()