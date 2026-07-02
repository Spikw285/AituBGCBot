from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.member import Member, MemberRole
from database.models.notification import Notification, NotificationKind, NotificationStatus
from services.member_service import list_members_by_role


log = logging.getLogger(__name__)


async def create_notification_record(
    session: AsyncSession,
    recipient: Member,
    title: str,
    body: str,
    kind: NotificationKind = NotificationKind.SYSTEM,
    sender_id: int | None = None,
) -> Notification:
    notification = Notification(
        recipient_id=recipient.id,
        sender_id=sender_id,
        kind=kind,
        title=title,
        body=body,
        status=NotificationStatus.PENDING,
    )
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


async def notify_member(
    bot: Bot,
    session: AsyncSession,
    recipient: Member,
    title: str,
    body: str,
    kind: NotificationKind = NotificationKind.SYSTEM,
    sender_id: int | None = None,
) -> Notification | None:
    if not recipient.is_active or not recipient.receive_notifications:
        return None

    notification = await create_notification_record(session, recipient, title, body, kind, sender_id)
    try:
        await bot.send_message(recipient.telegram_id, f"<b>{title}</b>\n\n{body}", parse_mode="HTML")
    except Exception:
        notification.status = NotificationStatus.FAILED
        await session.commit()
        await session.refresh(notification)
        raise

    notification.status = NotificationStatus.SENT
    notification.sent_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(notification)
    return notification


async def notify_role(
    bot: Bot,
    session: AsyncSession,
    role: MemberRole,
    title: str,
    body: str,
    kind: NotificationKind = NotificationKind.SYSTEM,
    sender_id: int | None = None,
) -> int:
    recipients = await list_members_by_role(session, role)
    sent = 0

    for recipient in recipients:
        try:
            if await notify_member(bot, session, recipient, title, body, kind, sender_id):
                sent += 1
        except Exception:
            log.exception("Failed to notify member tg_id=%d", recipient.telegram_id)

    return sent


async def notify_new_member(bot: Bot, session: AsyncSession, member: Member) -> int:
    title = "Новая регистрация"
    body = (
        f"{escape(member.full_name)} присоединился к боту.\n"
        f"Telegram ID: {member.telegram_id}\n"
        f"Роль: {escape(member.role.value)}\n"
        f"Уровень доверия: {escape(member.trust_level.value)}"
    )
    return await notify_role(bot, session, MemberRole.ADMIN, title, body, NotificationKind.REGISTRATION)
