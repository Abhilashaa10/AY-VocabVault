# backend/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# ─────────────────────────────────────────
# USERS TABLE
# ─────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    progress = relationship("UserProgress", back_populates="user")
    enrolled_domains = relationship("UserDomain", back_populates="user")


# ─────────────────────────────────────────
# DOMAINS TABLE
# ─────────────────────────────────────────
class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String)

    vocabulary = relationship("Vocabulary", back_populates="domain")


# ─────────────────────────────────────────
# VOCABULARY TABLE
# ─────────────────────────────────────────
class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    word = Column(String, nullable=False)
    definition = Column(Text, nullable=False)
    difficulty_level = Column(Integer, default=1)
    example_sentence = Column(Text)

    domain = relationship("Domain", back_populates="vocabulary")
    progress = relationship("UserProgress", back_populates="vocabulary")


# ─────────────────────────────────────────
# USER DOMAINS TABLE
# ─────────────────────────────────────────
class UserDomain(Base):
    __tablename__ = "user_domains"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    domain_id = Column(Integer, ForeignKey("domains.id"))
    enrolled_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="enrolled_domains")


# ─────────────────────────────────────────
# USER PROGRESS TABLE
# Heart of personalization
# ─────────────────────────────────────────
class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vocab_id = Column(Integer, ForeignKey("vocabulary.id"))

    mastery_score = Column(Float, default=0.0)
    times_seen = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    last_seen_at = Column(DateTime)

    user = relationship("User", back_populates="progress")
    vocabulary = relationship("Vocabulary", back_populates="progress")