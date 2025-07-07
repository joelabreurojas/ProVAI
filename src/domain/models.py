import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.infrastructure.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # teacher or student
    chats = relationship("Chat", back_populates="owner")
    chat_memberships = relationship("ChatMembership", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner = relationship("User", back_populates="chats")
    documents = relationship("Document", back_populates="chat")
    members = relationship("ChatMembership", back_populates="chat")
    history = relationship("History", back_populates="chat")


class ChatMember(Base):
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat = relationship("Chat", back_populates="members")
    user = relationship("User", back_populates="chat_memberships")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    chat = relationship("Chat", back_populates="documents")


class SessionHistory(Base):
    __tablename__ = "session_history"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    query = Column(String, nullable=False)
    response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    chat = relationship("Chat", back_populates="history")
