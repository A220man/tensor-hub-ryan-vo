# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-analyzer

## Roadmap

### core-analyzer — PHP Issue Analyzer Core Engine

Status: done

Acceptance:
- Parse PHP GitHub issues and extract structured data (version, OS, stack traces, error patterns)
- Classify issues by category: segfault, performance, memory, logic bug, platform-specific
- Generate reproducible test cases from issue descriptions
- Provide API endpoint to analyze new issue text

Implementation: `backend/app/services/analyzer.py`, `backend/app/models/schemas.py`, `backend/app/api/issues.py`

Tests: `backend/tests/test_analyzer.py`

### api-server — FastAPI Backend with SQLite

Status: done

Acceptance:
- FastAPI app with /api/issues endpoint for CRUD operations
- SQLite persistence with proper schema for issues, analyses, test cases
- Health check endpoint
- Pagination and filtering on issue list

Implementation: `backend/app/main.py`, `backend/app/api/issues.py`, `backend/app/api/health.py`, `backend/app/models/issue.py`, `backend/app/core/database.py`, `backend/app/core/config.py`, `backend/app/services/issue_service.py`

Tests: `backend/tests/test_api.py`, `backend/tests/conftest.py`

### frontend-dashboard — React Dashboard for Issue Analysis

Status: done

Acceptance:
- Dashboard listing issues with category, version, status
- Detail view showing stack trace, classification, suggested test case
- Create/import workflow for new GitHub issues
- Export analysis as JSON/Markdown

Implementation: `frontend/src/App.tsx`, `frontend/src/components/Dashboard.tsx`, `frontend/src/components/IssueCard.tsx`, `frontend/src/components/IssueDetail.tsx`, `frontend/src/components/IssueImport.tsx`, `frontend/src/hooks/useIssues.ts`, `frontend/src/api/client.ts`, `frontend/src/types/api.ts`

Tests: `frontend/src/components/IssueCard.test.tsx`, `frontend/src/components/Dashboard.test.tsx`

### auth-oidc — OIDC Authentication with Keycloak

Status: planned

Acceptance:
- Keycloak realm configuration
- Backend session management with HttpOnly cookies
- Frontend PKCE flow with in-memory tokens
- Role-based access (viewer, operator, admin)

### docker-compose — Docker Compose with Keycloak

Status: done

Acceptance:
- Backend and frontend Dockerfiles with non-root users
- compose.yaml with Keycloak and persistent volumes
- Health checks for all services
- Development profile binding to 127.0.0.1

Implementation: `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `compose.yaml`

### ci-pipeline — GitHub Actions CI Pipeline

Status: done

Acceptance:
- Backend pytest tests (minimum 12 meaningful tests)
- Frontend npm build and vitest tests (minimum 3 tests)
- Docker build for both services
- Lock file validation

Implementation: `.github/workflows/ci.yml`

### docs-packaging — Documentation and Packaging

Status: done

Acceptance:
- README with install/run/test steps and architecture diagram
- portfolio.json with schema_version=1
- LICENSE MIT, CHANGELOG.md
- .env.example with blank credentials

Implementation: `README.md`, `portfolio.json`, `LICENSE`, `CHANGELOG.md`, `.env.example`, `.gitignore`, `pyproject.toml`

