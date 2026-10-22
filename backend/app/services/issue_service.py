from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.issue import Issue, IssueCategory, IssueStatus
from backend.app.models.schemas import IssueCreate, IssueUpdate, IssueListResponse, IssueResponse
from backend.app.services.analyzer import PHPIssueAnalyzer
import json


class IssueService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analyzer = PHPIssueAnalyzer()

    async def create(self, issue_data: IssueCreate) -> Issue:
        issue = Issue(
            github_number=issue_data.github_number,
            title=issue_data.title,
            body=issue_data.body,
            html_url=issue_data.html_url,
            php_version=issue_data.php_version,
            os=issue_data.os,
            comments_count=issue_data.comments_count,
        )
        self.session.add(issue)
        await self.session.flush()
        await self.session.refresh(issue)
        return issue

    async def create_with_analysis(self, issue_data: IssueCreate):
        # Create issue
        issue = await self.create(issue_data)

        # Analyze
        from backend.app.models.schemas import AnalyzeRequest
        analyze_request = AnalyzeRequest(
            title=issue_data.title,
            body=issue_data.body,
            php_version=issue_data.php_version,
            os=issue_data.os,
        )
        analysis_data, test_case_data = self.analyzer.analyze(analyze_request)

        # Save analysis
        from backend.app.models.issue import Analysis
        analysis = Analysis(
            issue_id=issue.id,
            classification=analysis_data.classification,
            stack_trace=analysis_data.stack_trace,
            error_patterns=json.dumps(analysis_data.error_patterns) if analysis_data.error_patterns else None,
            root_cause=analysis_data.root_cause,
            suggested_fix=analysis_data.suggested_fix,
            confidence=analysis_data.confidence,
        )
        self.session.add(analysis)

        # Save test case if generated
        if test_case_data:
            from backend.app.models.issue import TestCase
            test_case = TestCase(
                issue_id=issue.id,
                language=test_case_data.language,
                code=test_case_data.code,
                description=test_case_data.description,
                expected_behavior=test_case_data.expected_behavior,
            )
            self.session.add(test_case)

        # Update issue status and category
        issue.category = analysis_data.classification
        issue.status = IssueStatus.ANALYZED if not test_case_data else IssueStatus.TEST_GENERATED

        await self.session.commit()
        await self.session.refresh(issue)
        return issue

    async def get(self, issue_id: int) -> Issue | None:
        result = await self.session.execute(select(Issue).where(Issue.id == issue_id))
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        category: str | None = None,
        status: str | None = None,
    ) -> IssueListResponse:
        query = select(Issue)
        if category:
            query = query.where(Issue.category == category)
        if status:
            query = query.where(Issue.status == status)

        total_result = await self.session.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar_one()

        query = query.order_by(Issue.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        items = result.scalars().all()

        return IssueListResponse(
            items=[IssueResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update(self, issue_id: int, issue_data: IssueUpdate) -> Issue | None:
        issue = await self.get(issue_id)
        if not issue:
            return None
        update_data = issue_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(issue, field, value)
        await self.session.commit()
        await self.session.refresh(issue)
        return issue

    async def delete(self, issue_id: int) -> bool:
        issue = await self.get(issue_id)
        if not issue:
            return False
        await self.session.delete(issue)
        await self.session.commit()
        return True

    async def reanalyze(self, issue_id: int) -> Issue | None:
        issue = await self.get(issue_id)
        if not issue:
            return None

        from backend.app.models.schemas import AnalyzeRequest
        analyze_request = AnalyzeRequest(
            title=issue.title,
            body=issue.body,
            php_version=issue.php_version,
            os=issue.os,
        )
        analysis_data, test_case_data = self.analyzer.analyze(analyze_request)

        # Delete old analyses and test cases
        from backend.app.models.issue import Analysis, TestCase
        await self.session.execute(select(Analysis).where(Analysis.issue_id == issue_id))
        await self.session.execute(select(TestCase).where(TestCase.issue_id == issue_id))

        # Save new analysis
        analysis = Analysis(
            issue_id=issue.id,
            classification=analysis_data.classification,
            stack_trace=analysis_data.stack_trace,
            error_patterns=json.dumps(analysis_data.error_patterns) if analysis_data.error_patterns else None,
            root_cause=analysis_data.root_cause,
            suggested_fix=analysis_data.suggested_fix,
            confidence=analysis_data.confidence,
        )
        self.session.add(analysis)

        # Save new test case if generated
        if test_case_data:
            test_case = TestCase(
                issue_id=issue.id,
                language=test_case_data.language,
                code=test_case_data.code,
                description=test_case_data.description,
                expected_behavior=test_case_data.expected_behavior,
            )
            self.session.add(test_case)

        issue.category = analysis_data.classification
        issue.status = IssueStatus.ANALYZED if not test_case_data else IssueStatus.TEST_GENERATED

        await self.session.commit()
        await self.session.refresh(issue)
        return issue