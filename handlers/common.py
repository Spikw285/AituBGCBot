from __future__ import annotations

import logging
from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from database.base import AsyncSession
from database.models.member import Member, MemberRole
from services.member_service import (
    get_or_create_member,
    set_notifications_enabled,
)
from services.notification_service import notify_new_member

log = logging.getLogger(__name__)

router = Router(name="core")


def _role_label(role: MemberRole) -> str:
    labels = {
        MemberRole.GUEST: "гость",
        MemberRole.MEMBER: "участник",
        MemberRole.GM: "гейм-мастер",
        MemberRole.ADMIN: "администратор",
    }
    return labels.get(role, role.value)


async def _ensure_member(message: Message, session: AsyncSession) -> tuple[Member | None, bool]:
    if message.from_user is None:
        return None, False

    member, created = await get_or_create_member(
        session=session,
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
    )
    return member, created


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return

    member, created = await _ensure_member(message, session)
    if member is None:
        return

    if created:
        log.info("Registered new member tg_id=%d", message.from_user.id)
        try:
            await notify_new_member(message.bot, session, member)
        except Exception:
            log.exception("Failed to notify admins about registration tg_id=%d", message.from_user.id)

    await message.answer(
        "<b>Добро пожаловать в клуб AITU Board Games</b>\n\n"
        f"Профиль: {_role_label(member.role)}\n"
        f"Уровень доверия: {member.trust_level.value}\n\n"
        "Доступные команды:\n"
        "/help - справка\n"
        "/profile - мой профиль\n"
        "/notifications_on - включить уведомления\n"
        "/notifications_off - выключить уведомления\n"
        "/game_request - запрос на игру\n"
        "/gm_request - запрос к ГМу\n"
        "/ttrpg_signup - запись на НРИ",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Справка</b>\n\n"
        "/start - регистрация и приветствие\n"
        "/profile - показать роль и уровень доверия\n"
        "/notifications_on - включить уведомления\n"
        "/notifications_off - выключить уведомления\n"
        "/game_request - запросить конкретную игру\n"
        "/gm_request - запросить помощь ГМа\n"
        "/ttrpg_signup - записаться на НРИ-сессию",
        parse_mode="HTML",
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return

    member, created = await _ensure_member(message, session)
    if member is None:
        return

    if created:
        try:
            await notify_new_member(message.bot, session, member)
        except Exception:
            log.exception("Failed to notify admins about registration tg_id=%d", message.from_user.id)

    await message.answer(
        "<b>Мой профиль</b>\n\n"
        f"Имя: {escape(member.full_name)}\n"
        f"Роль: {_role_label(member.role)}\n"
        f"Уровень доверия: {member.trust_level.value}\n"
        f"Уведомления: {'включены' if member.receive_notifications else 'выключены'}",
        parse_mode="HTML",
    )


@router.message(Command("notifications_on"))
async def cmd_notifications_on(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return

    member, created = await _ensure_member(message, session)
    if member is None:
        return

    if created:
        try:
            await notify_new_member(message.bot, session, member)
        except Exception:
            log.exception("Failed to notify admins about registration tg_id=%d", message.from_user.id)

    await set_notifications_enabled(session, member, True)
    await message.answer("Уведомления включены.")


@router.message(Command("notifications_off"))
async def cmd_notifications_off(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return

    member, created = await _ensure_member(message, session)
    if member is None:
        return

    if created:
        try:
            await notify_new_member(message.bot, session, member)
        except Exception:
            log.exception("Failed to notify admins about registration tg_id=%d", message.from_user.id)

    await set_notifications_enabled(session, member, False)
    await message.answer("Уведомления выключены.")
