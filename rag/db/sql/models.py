"""
SQL models
"""

from datetime import UTC, datetime
from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


class Chat(Base):
    """
    Chat model
    """

    __tablename__ = "chat"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )

    messages: Mapped[List["Message"]] = relationship(
        cascade="all, delete-orphan", lazy=True
    )


class Message(Base):
    """
    Message model
    """

    __tablename__ = "message"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chat.id"))
    is_system: Mapped[bool] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
