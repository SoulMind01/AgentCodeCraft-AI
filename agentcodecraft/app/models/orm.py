"""
SQLAlchemy ORM models.
"""
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    organization = Column(String, nullable=True)

    sessions = relationship("RefactorSession", back_populates="user", cascade="all,delete")


class PolicyProfile(Base):
    __tablename__ = "policy_profiles"

    policy_profile_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    version = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rules = relationship("PolicyRule", back_populates="profile", cascade="all,delete-orphan")


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    rule_id = Column(String, primary_key=True, index=True)
    policy_profile_id = Column(String, ForeignKey("policy_profiles.policy_profile_id"))
    rule_key = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    expression = Column(String, nullable=False)
    severity = Column(String, default="medium", nullable=False)
    auto_fixable = Column(Boolean, default=False)

    profile = relationship("PolicyProfile", back_populates="rules")


class RefactorSession(Base):
    __tablename__ = "refactor_sessions"

    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    repo = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    language = Column(String, nullable=False)
    policy_profile_id = Column(String, ForeignKey("policy_profiles.policy_profile_id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="pending", nullable=False)

    user = relationship("User", back_populates="sessions")
    policy_profile = relationship("PolicyProfile")
    suggestions = relationship(
        "RefactorSuggestion", back_populates="session", cascade="all,delete-orphan"
    )
    metrics = relationship(
        "ComplianceMetric", back_populates="session", cascade="all,delete-orphan", uselist=False
    )


class RefactorSuggestion(Base):
    __tablename__ = "refactor_suggestions"

    suggestion_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("refactor_sessions.session_id"))
    file_path = Column(String, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    original_code = Column(Text, nullable=False)
    proposed_code = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.5, nullable=False)

    session = relationship("RefactorSession", back_populates="suggestions")


class ComplianceMetric(Base):
    __tablename__ = "compliance_metrics"

    metric_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("refactor_sessions.session_id"))
    policy_score = Column(Float, nullable=False)
    complexity_delta = Column(Float, nullable=False)
    test_pass_rate = Column(Float, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    token_usage = Column(Integer, nullable=False)

    session = relationship("RefactorSession", back_populates="metrics")


