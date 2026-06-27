"""
Модели для модуля запросов участников
Owner: Spikw285

GameRequest - участник хочет сыграть в конкретную игру (ГМ приносит из шкафа)
GMRequest - участник не знает во что сыграть / нужна помощь с правилами
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

class RequestStatus(PyEnum):
    """Статус любого запроса участника - общий для GameRequest и GMRequest"""
    PENDING  = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class GMNeedType(PyEnum):
    """Тим запроса к ГМу"""
    RECOMMEND = "recommend"
    RULES     = "rules"

class GameRequest(Base):
    """
    Запрос на конкретную игру. Участник указывает игру, желаемую дату, и опциональный комментарий.

    ГМ видит запрос и принимает/отклоняет
    """
    __tablename__ = "game_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # TODO: раскомментировать ForeignKey после появления database/models/members.py
    member_id: Mapped[int] = mapped_column(
        # ForeignKey("members.id"),
        Integer,
        nullable=False,
        comment="FK -> members.id. Убрать коммент после реализации member.py",
    )

    # TODO: раскомментировать ForeignKey после появления database/models/games.py
    game_id: Mapped[int] = mapped_column(
        # ForeignKey("games.id"),
        Integer,
        nullable=False,
        comment="FK -> games.id. Убрать коммент после реализации game.py",
    )

    desired_date: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Свободный текст для любого формата даты",
    )

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus, name="request_status"),
        default=RequestStatus.PENDING,
        nullable=False,
    )

    # TODO: раскомментировать ForeignKey после member.py
    handled_by: Mapped[int | None] = mapped_column(
        # ForeignKey("members.id")
        Integer,
        nullable=True,
        comment="Какой ГМ принял/отклонил. FK -> members.id",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # TODO: раскомментировать relationship после появления Member и Game
    # member = relationship("Member", foreign_keys=[member_id])
    # game = relationship("Game", foreign_keys=[game_id])
    # handled_by = relationship("Member",foreign_keys=[handled_by])

class GMRequest(Base):
    """
    Запрос к ГМу. Два типа запроса: рекомендация игры (recommend) и объяснения правил (rules)
    """

    __tablename__ = "gm_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    member_id: Mapped[int] = mapped_column(
        # ForeignKey("members.id"),
        Integer,
        nullable=False,
        comment="FK -> members.id",
    )

    need_type: Mapped[GMNeedType] = mapped_column(
        SQLEnum(GMNeedType, name="gm_need_type"),
        nullable=False,
    )

    # Только для need_type == RULES, поэтому может иметь NULL
    game_id: Mapped[int | None] = mapped_column(
        # ForeignKey("games.id"),
        Integer,
        nullable=True,
        comment="FK -> games.id. Заполняется только для need_type=RULES",
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[RequestStatus] = mapped_column(
        SQLEnum(RequestStatus, name="request_status"),
        default=RequestStatus.PENDING,
        nullable=False,
    )

    handled_by: Mapped[int | None] = mapped_column(
        # ForeignKey("members.id"),
        Integer,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # TODO: раскомментировать после Member и Game
    # member = relationship("Member", foreign_keys=[member_id])
    # game = relationship("Game", foreign_keys=[game_id])
    # handled_by = relationship("Member",foreign_keys=[handled_by])
