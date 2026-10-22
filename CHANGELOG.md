# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-22

### Added
- Initial release of PHP Issue Analyzer
- FastAPI backend with SQLite persistence
- Issue CRUD API with pagination and filtering
- Deterministic PHP issue classification engine (7 categories)
- Stack trace and error pattern extraction
- Root cause analysis with suggested fixes
- Reproducible test case generation for known issue patterns
- React + TypeScript + Vite frontend
- Issue dashboard with category/status filtering
- Issue detail view with analysis results
- Import workflow for GitHub issues and manual entry
- Docker Compose with Keycloak for OIDC authentication
- GitHub Actions CI pipeline

### Security
- Non-root Docker users
- HttpOnly cookie sessions (planned for OIDC integration)
- Input validation on all API endpoints

## [Unreleased]

### Planned
- Full OIDC authentication implementation
- Advanced ML-based classification (optional LLM)
- Batch issue import from GitHub API
- Export to PHP test suite format (.phpt)
- Real-time analysis progress
- Comparison view for similar issues