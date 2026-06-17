from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

class RequestStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class GameRequest(Base):
    """Участник хочет сыграть в конкретную игру, и зовёт ГМа"""
    __tablename__ = "game_requests"

    id:             Mapped[int]     = mapped_column(Integer, primary_key=True)
    member_id:      Mapped[int]     = mapped_column(ForeignKey("members.id"))
    game_id:        Mapped[int]     = mapped_column(ForeignKey("games.id"))
    desired_date:   Mapped[str]     = mapped_column(String(64), nullable=True)
    comment:        Mapped[str]     = mapped_column(Text, nullable=True)
    status:         Mapped[str]     = mapped_column(
                                        Enum(RequestStatus),
                                        default=RequestStatus.PENDING
                                        )
    created_at:     Mapped[datetime] = mapped_column(
                                        DateTime(timezone=True),
                                        default=lambda: datetime.now(timezone.utc)
                                        )
    member = relationship("Member", back_populates="game_requests")
    game   = relationship("Game")

class GMRequest(Base):
    """Участник хочет сыграть в игру, но не знает в какую или нужна помощь с правилами"""
    __tablename__ = "gm_requests"

    id:                 Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id:          Mapped[int] = mapped_column(ForeignKey("members.id"))
    preferred_game_id:  Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=True)
    need_type:          Mapped[str] = mapped_column(String(32))
    notes:              Mapped[str] = mapped_column(Text, nullable=True)
    status:             Mapped[str] = mapped_column(
                                        Enum(RequestStatus),
                                        default=RequestStatus.PENDING
                                        )
    created_at:         Mapped[datetime] = mapped_column(
                                        DateTime(timezone=True),
                                        default=lambda: datetime.now(timezone.utc)
                                        )

    member         = relationship("Member", back_populates="gm_requests")
    preferred_game = relationship("Game", foreign_keys=[preferred_game_id])