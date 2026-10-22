from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class IssueCategory(str, PyEnum):
    SEGFAULT = "segfault"
    PERFORMANCE = "performance"
    MEMORY = "memory"
    LOGIC_BUG = "logic_bug"
    PLATFORM_SPECIFIC = "platform_specific"
    FEATURE_REQUEST = "feature_request"
    UNKNOWN = "unknown"


class IssueStatus(str, PyEnum):
    NEW = "new"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    TEST_GENERATED = "test_generated"
    CLOSED = "closed"


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    github_number = Column(Integer, unique=True, index=True, nullable=True)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    html_url = Column(String(500), nullable=True)
    php_version = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    comments_count = Column(Integer, default=0)
    category = Column(String(50), default=IssueCategory.UNKNOWN.value, index=True)
    status = Column(String(50), default=IssueStatus.NEW.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    analyses = relationship("Analysis", back_populates="issue", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="issue", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_issues_category_status", "category", "status"),
        Index("ix_issues_created_at", "created_at"),
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    classification = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    error_patterns = Column(Text, nullable=True)  # JSON array
    root_cause = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    confidence = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    issue = relationship("Issue", back_populates="analyses")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    language = Column(String(50), default="php")
    code = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    status = Column(String(50), default="generated")  # generated, verified, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    issue = relationship("Issue", back_populates="test_cases")