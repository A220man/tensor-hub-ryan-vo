from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.app.core.database import get_session
from backend.app.services.issue_service import IssueService
from backend.app.models.schemas import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueListResponse,
    AnalyzeRequest,
    AnalyzeResponse,
)
from backend.app.models.issue import IssueCategory, IssueStatus


router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_data: IssueCreate,
    session: AsyncSession = Depends(get_session),
):
    service = IssueService(session)
    issue = await service.create_with_analysis(issue_data)
    return IssueResponse.model_validate(issue)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_issue(
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_session),
):
    """Analyze an issue without persisting it."""
    from backend.app.services.analyzer import PHPIssueAnalyzer
    from backend.app.models.issue import Issue
    from backend.app.models.schemas import AnalysisResponse, TestCaseResponse
    from datetime import datetime

    analyzer = PHPIssueAnalyzer()
    analysis_data, test_case_data = analyzer.analyze(request)

    # Create a temporary issue object for response
    temp_issue = Issue(
        id=0,
        github_number=None,
        title=request.title,
        body=request.body,
        html_url=None,
        php_version=request.php_version,
        os=request.os,
        comments_count=0,
        category=analysis_data.classification,
        status=IssueStatus.ANALYZED if not test_case_data else IssueStatus.TEST_GENERATED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    response = AnalyzeResponse(
        issue=IssueResponse.model_validate(temp_issue),
        analysis=AnalysisResponse(
            id=0,
            issue_id=0,
            classification=analysis_data.classification,
            stack_trace=analysis_data.stack_trace,
            error_patterns=analysis_data.error_patterns,
            root_cause=analysis_data.root_cause,
            suggested_fix=analysis_data.suggested_fix,
            confidence=analysis_data.confidence,
            created_at=datetime.utcnow(),
        ),
        test_case=TestCaseResponse(
            id=0,
            issue_id=0,
            language=test_case_data.language,
            code=test_case_data.code,
            description=test_case_data.description,
            expected_behavior=test_case_data.expected_behavior,
            status="generated",
            created_at=datetime.utcnow(),
        ) if test_case_data else None,
    )
    return response


@router.get("", response_model=IssueListResponse)
async def list_issues(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[IssueCategory] = Query(None),
    status: Optional[IssueStatus] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    service = IssueService(session)
    return await service.list(page, page_size, category, status)


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = IssueService(session)
    issue = await service.get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return IssueResponse.model_validate(issue)


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int,
    issue_data: IssueUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = IssueService(session)
    issue = await service.update(issue_id, issue_data)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return IssueResponse.model_validate(issue)


@router.post("/{issue_id}/reanalyze", response_model=IssueResponse)
async def reanalyze_issue(
    issue_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = IssueService(session)
    issue = await service.reanalyze(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return IssueResponse.model_validate(issue)


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    issue_id: int,
    session: AsyncSession = Depends(get_session),
):
    service = IssueService(session)
    deleted = await service.delete(issue_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Issue not found")