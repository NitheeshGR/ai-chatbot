# Database models: Conversation and Message tables
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db import Base


class Conversation(Base):
    """Stores each chat conversation with a title and timestamps."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # One conversation has many messages — deleting a conversation deletes its messages
    messages = relationship(
        "Message", backref="conversation", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Conversation {self.id}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Message(Base):
    """Stores a single message (user or assistant) inside a conversation."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    # Links to the conversation this message belongs to
    conversation_id = Column(
        Integer, ForeignKey("conversations.id"), nullable=False
    )
    # "user" or "assistant"
    role = Column(String(20), nullable=False)
    # The actual message text
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Message {self.id}: {self.role}>"

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
