from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class MemberRole(PyEnum):
    GUEST = "guest"
    MEMBER = "member"
    GM = "gm"
    ADMIN = "admin"


class TrustLevel(PyEnum):
    NEW = "new"
    VERIFIED = "verified"
    TRUSTED = "trusted"
    CORE = "core"


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, name="member_role"),
        default=MemberRole.MEMBER,
        nullable=False,
    )
    trust_level: Mapped[TrustLevel] = mapped_column(
        Enum(TrustLevel, name="trust_level"),
        default=TrustLevel.NEW,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    receive_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    game_requests = relationship("GameRequest", back_populates="member", cascade="all, delete-orphan")
    gm_requests = relationship("GMRequest", back_populates="member", cascade="all, delete-orphan")
    borrow_logs = relationship(
        "BorrowLog",
        back_populates="borrower",
        foreign_keys="BorrowLog.borrower_id",
    )
    notifications = relationship(
        "Notification",
        back_populates="recipient",
        foreign_keys="Notification.recipient_id",
        cascade="all, delete-orphan",
    )
    led_campaigns = relationship("Campaign", back_populates="dm")
    dm_sessions = relationship("Session", back_populates="dm")
    ttrpg_signups = relationship("TTRPGSignup", back_populates="member", cascade="all, delete-orphan")
