from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, func

from datetime import datetime
from typing import Optional
class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(36), nullable=False)
    surname: Mapped[str] = mapped_column(String(36), nullable=False)
    email: Mapped[str] = mapped_column(String(144), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)

    users_chats = relationship("UsersChats", back_populates="users")
    users_messages = relationship("Messages", back_populates="users")

class Chats(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_name: Mapped[str] = mapped_column(String(72), nullable=False)

    users_chats = relationship("UsersChats", back_populates="chats")
    chat_messages = relationship("Messages", back_populates="chats")

class UsersChats(Base):
    __tablename__ = "userschats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    chats = relationship("Chats", back_populates="users_chats")
    users = relationship("Users", back_populates="users_chats")

class Messages(Base):
    __tablename__="messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    content: Mapped[str] = mapped_column(String(4000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    reply_message_id: Mapped[Optional[int]] = mapped_column(ForeignKey('messages.id'), nullable=True)
    
    chats = relationship("Chats", back_populates="chat_messages")
    users = relationship("Users", back_populates="users_messages")
    reply_messages = relationship("Messages", remote_side=[id], backref="replies")