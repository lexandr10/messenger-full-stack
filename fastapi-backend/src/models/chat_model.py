from sqlalchemy import (
    func,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    String,
    Boolean,
    Integer,
    PrimaryKeyConstraint,
)
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from src.models.user_model import Base


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    user2_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.current_date(), nullable=False
    )
    __table_args__ = (
        UniqueConstraint("user1_id", "user2_id", name="uq_conversation_pair"),
        Index("ix_conversations_users", "user1_id", "user2_id"),
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reply_to_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("messages.id"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.current_date(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.current_date(),
        onupdate=func.current_date(),
        nullable=False,
    )
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    conversation = relationship("Conversation", back_populates="messages")
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment",
        back_populates="message",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), index=True
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    storage: Mapped[str] = mapped_column(String(20), nullable=False, default="local")
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False
    )

    message = relationship("Message", back_populates="attachments")


class MessageRead(Base):
    __tablename__ = "message_reads"

    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint("message_id", "user_id", name="pk_message_reads"),
    )
