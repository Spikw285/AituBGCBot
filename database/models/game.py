from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class GameCopyStatus(PyEnum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    MAINTENANCE = "maintenance"
    LOST = "lost"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_players: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_players: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    copies = relationship("GameCopy", back_populates="game", cascade="all, delete-orphan")


class GameCopy(Base):
    __tablename__ = "game_copies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    inventory_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    status: Mapped[GameCopyStatus] = mapped_column(
        Enum(GameCopyStatus, name="game_copy_status"),
        default=GameCopyStatus.AVAILABLE,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    game = relationship("Game", back_populates="copies")
    borrow_logs = relationship("BorrowLog", back_populates="game_copy", cascade="all, delete-orphan")

