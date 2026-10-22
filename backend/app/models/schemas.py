from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class IssueCategory(str, Enum):
    SEGFAULT = "segfault"
    PERFORMANCE = "performance"
    MEMORY = "memory"
    LOGIC_BUG = "logic_bug"
    PLATFORM_SPECIFIC = "platform_specific"
    FEATURE_REQUEST = "feature_request"
    UNKNOWN = "unknown"


class IssueStatus(str, Enum):
    NEW = "new"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    TEST_GENERATED = "test_generated"
    CLOSED = "closed"


class TestCaseStatus(str, Enum):
    GENERATED = "generated"
    VERIFIED = "verified"
    FAILED = "failed"


class IssueBase(BaseModel):
    github_number: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=500)
    body: str
    html_url: Optional[HttpUrl] = None
    php_version: Optional[str] = None
    os: Optional[str] = None
    comments_count: int = 0


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    body: Optional[str] = None
    php_version: Optional[str] = None
    os: Optional[str] = None
    category: Optional[IssueCategory] = None
    status: Optional[IssueStatus] = None


class IssueResponse(IssueBase):
    id: int
    category: IssueCategory
    status: IssueStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IssueListResponse(BaseModel):
    items: List[IssueResponse]
    total: int
    page: int
    page_size: int


class AnalysisBase(BaseModel):
    classification: str
    stack_trace: Optional[str] = None
    error_patterns: Optional[List[str]] = None
    root_cause: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: int = Field(ge=0, le=100, default=0)


class AnalysisCreate(AnalysisBase):
    pass


class AnalysisResponse(AnalysisBase):
    id: int
    issue_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TestCaseBase(BaseModel):
    language: str = "php"
    code: str
    description: Optional[str] = None
    expected_behavior: Optional[str] = None


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseResponse(TestCaseBase):
    id: int
    issue_id: int
    status: TestCaseStatus
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    title: str
    body: str
    php_version: Optional[str] = None
    os: Optional[str] = None


class AnalyzeResponse(BaseModel):
    issue: IssueResponse
    analysis: AnalysisResponse
    test_case: Optional[TestCaseResponse] = None