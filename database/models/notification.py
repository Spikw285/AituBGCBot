from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class NotificationKind(PyEnum):
    SYSTEM = "system"
    REGISTRATION = "registration"
    ROLE_CHANGE = "role_change"
    TRUST_CHANGE = "trust_change"
    REQUEST = "request"


class NotificationStatus(PyEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True)
    kind: Mapped[NotificationKind] = mapped_column(
        Enum(NotificationKind, name="notification_kind"),
        default=NotificationKind.SYSTEM,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status"),
        default=NotificationStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recipient = relationship("Member", foreign_keys=[recipient_id], back_populates="notifications")
    sender = relationship("Member", foreign_keys=[sender_id])

