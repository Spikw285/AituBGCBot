from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class BorrowLog(Base):
    __tablename__ = "borrow_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_copy_id: Mapped[int] = mapped_column(ForeignKey("game_copies.id"), nullable=False)
    borrower_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    issued_by_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True)
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    game_copy = relationship("GameCopy", back_populates="borrow_logs")
    borrower = relationship("Member", foreign_keys=[borrower_id], back_populates="borrow_logs")
    issuer = relationship("Member", foreign_keys=[issued_by_id])

