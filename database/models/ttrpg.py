"""
Модели для НРИ систем
Owner: Spikw285

TTRPGSystem     - справочник систем
DMProfile       - профиль ДМа
DMProfileSystem - какие системы водит ДМ (many-to-many)
Campaign        - тип сессии (Кампания или ваншот)
Session         - конкретная сессия в рамках кампании
TTRPGSignup     - заявка участника на кампанию
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database.base import Base


class CampaignType(PyEnum):
    CAMPAIGN = "campaign"
    ONESHOT  = "oneshot"

class CampaignStatus(PyEnum):
    RECRUITING  = "recruiting"
    IN_PROGRESS = "in_progress"
    COMPLETED   = "completed"
    CANCELLED   = "cancelled"

class SignupStatus(PyEnum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    REJECTED  = "rejected"

class TTRPGSystem(Base):
    """
    Справочник НРИ систем. Каждое издание - отдельная запись.

    Наполняется через seed.py
    """
    __tablename__ = "ttrpg_systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)

class DMProfile(Base):
    """
    Профиль ДМа.
    Один участник может иметь только один ДМ профиль (unique member_id)
    """
    __tablename__ = "dm_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # TODO: раскомментировать после реализации member.py
    member_id: Mapped[int] = mapped_column(
        # ForeignKey("members.id"),
        Integer,
        nullable=False,
        unique=True,
        comment="FK -> members.id, unique",
    )

    experience: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_accepting: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Связь many-to-many через DMProfileSystem
    systems: Mapped[list["DMProfileSystem"]] = relationship(back_populates="dm_profiles")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="dm")

    # TODO: раскомментировать после member.py
    # member = relationship("Member", foreign_keys=[member_id])

class DMProfileSystem(Base):
    """
    Связка ДМ-профиля с системами которы он водит.

    Составной первичный ключ - пара (dm_profile_id, system_id) должна быть уникальной
    """
    __tablename__ = "dm_profile_systems"

    dm_profile_id: Mapped[int] = mapped_column(
        ForeignKey("dm_profiles.id"), primary_key=True
    )
    system_id: Mapped[int] = mapped_column(
        ForeignKey("ttrpg_systems.id"), primary_key=True
    )

    dm_profile: Mapped["DMProfile"] = relationship(back_populates="systems")
    system: Mapped["TTRPGSystem"] = relationship()

class Campaign(Base):
    """Кампания или ваншот, который ведёт ДМ"""
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dm_id: Mapped[int] = mapped_column(ForeignKey("dm_profiles.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(128), nullable=False)
    system_id: Mapped[int] = mapped_column(ForeignKey("ttrpg_systems.id"), nullable=False)

    type:  Mapped[CampaignType] = mapped_column(
        SQLEnum(CampaignType, name="campaign_type"), nullable=False
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False)
    requirements: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Опыт игроков, возрастные ограничения и т.п."
    )

    status: Mapped[CampaignStatus] = mapped_column(
        SQLEnum(CampaignStatus, name="campaign_status"),
        default=CampaignStatus.RECRUITING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    dm: Mapped["DMProfile"] = relationship(back_populates="campaigns")
    system: Mapped["TTRPGSystem"] = relationship()
    sessions: Mapped[list["Session"]] = relationship(back_populates="campaign")
    signups: Mapped[list["TTRPGSignup"]] = relationship(back_populates="campaign")

class Session(Base):
    """Конкретная сессия в рамках кампании"""
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    session_number: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="sessions")

class TTRPGSignup(Base):
    """Заявка участника на кампанию или ваншот"""
    __tablename__ = "ttrpg_signups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)

    # TODO: раскомментировать после имплементации member.py
    member_id: Mapped[int] = mapped_column(
        # ForeignKey("members.id"),
        Integer,
        nullable=False,
        comment="FK -> members.id",
    )

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[SignupStatus] = mapped_column(
        SQLEnum(SignupStatus, name="signup_status"),
        default=SignupStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="signups")
    # TODO: раскомментировать после имплементации member.py
    # member = relationship("Member", foreign_keys=[member_id])