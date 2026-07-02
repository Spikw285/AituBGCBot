from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class SessionType(PyEnum):
    CAMPAIGN = "campaign"
    ONESHOT = "oneshot"


class SignupStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    system: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dm_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    dm = relationship("Member", back_populates="led_campaigns")
    sessions = relationship("Session", back_populates="campaign", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "ttrpg_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    system: Mapped[str] = mapped_column(String(128), nullable=False)
    session_type: Mapped[SessionType] = mapped_column(
        Enum(SessionType, name="session_type"),
        default=SessionType.ONESHOT,
        nullable=False,
    )
    dm_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    max_players: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    campaign = relationship("Campaign", back_populates="sessions")
    dm = relationship("Member", back_populates="dm_sessions")
    signups = relationship("TTRPGSignup", back_populates="session", cascade="all, delete-orphan")


class TTRPGSignup(Base):
    __tablename__ = "ttrpg_signups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("ttrpg_sessions.id"), nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SignupStatus] = mapped_column(
        Enum(SignupStatus, name="signup_status"),
        default=SignupStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session = relationship("Session", back_populates="signups")
    member = relationship("Member", back_populates="ttrpg_signups")
