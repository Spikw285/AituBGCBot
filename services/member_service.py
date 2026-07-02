from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.member import Member, MemberRole, TrustLevel


DEFAULT_TRUST_BY_ROLE: dict[MemberRole, TrustLevel] = {
    MemberRole.GUEST: TrustLevel.NEW,
    MemberRole.MEMBER: TrustLevel.VERIFIED,
    MemberRole.GM: TrustLevel.TRUSTED,
    MemberRole.ADMIN: TrustLevel.CORE,
}


async def get_member_by_tg_id(session: AsyncSession, telegram_id: int) -> Member | None:
    result = await session.execute(select(Member).where(Member.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_member_by_id(session: AsyncSession, member_id: int) -> Member | None:
    result = await session.execute(select(Member).where(Member.id == member_id))
    return result.scalar_one_or_none()


async def list_members_by_role(session: AsyncSession, role: MemberRole) -> list[Member]:
    result = await session.execute(select(Member).where(Member.role == role, Member.is_active.is_(True)))
    return list(result.scalars().all())


async def get_or_create_member(
    session: AsyncSession,
    telegram_id: int,
    full_name: str,
    username: str | None = None,
    role: MemberRole = MemberRole.MEMBER,
) -> tuple[Member, bool]:
    member = await get_member_by_tg_id(session, telegram_id)
    created = False
    dirty = False

    if member is None:
        member = Member(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            role=role,
            trust_level=DEFAULT_TRUST_BY_ROLE[role],
        )
        session.add(member)
        created = True
    else:
        if member.full_name != full_name:
            member.full_name = full_name
            dirty = True
        if member.username != username:
            member.username = username
            dirty = True

    if created or dirty:
        await session.commit()
        await session.refresh(member)
    return member, created


async def set_member_role(session: AsyncSession, member: Member, role: MemberRole) -> Member:
    member.role = role
    member.trust_level = DEFAULT_TRUST_BY_ROLE[role]
    await session.commit()
    await session.refresh(member)
    return member


async def set_trust_level(session: AsyncSession, member: Member, trust_level: TrustLevel) -> Member:
    member.trust_level = trust_level
    await session.commit()
    await session.refresh(member)
    return member


async def set_notifications_enabled(session: AsyncSession, member: Member, enabled: bool) -> Member:
    member.receive_notifications = enabled
    await session.commit()
    await session.refresh(member)
    return member


def is_staff(member: Member) -> bool:
    return member.role in {MemberRole.GM, MemberRole.ADMIN}


def is_core_member(member: Member) -> bool:
    return member.trust_level in {TrustLevel.TRUSTED, TrustLevel.CORE}
