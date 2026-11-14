# Changelog

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

### Fixed
- Syntax error in generic test case template generation (missing return statement, incorrect string concatenation)
- All 22 analyzer tests pass; 32 backend tests pass; 11 frontend tests pass

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

### Added
- Complete memory issue classification support in PHPIssueAnalyzer
  - Memory leak detection with circular reference test case generation
  - Out of memory (OOM) handling with chunked processing test case
  - memory_limit configuration analysis with limit tracking test case
  - Generic memory issue fallback with profiling guidance
- Root cause analysis and suggested fixes for memory issues (leak, OOM, memory_limit, generic)
- 4 new analyzer tests for memory classification (leak, OOM, memory_limit, generic)
- 22 total analyzer tests, 32 total backend tests

### Fixed
- Case-sensitivity bug in PHPIssueAnalyzer JIT handler detection (both root cause analysis and test case generation)
- Added test coverage for lowercase JIT handler patterns

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

### Added
- Automatic PHP version detection from issue text (supports full version "8.3.1" and major.minor "8.2")
- Automatic OS detection from issue text (Linux distros, Windows, macOS/Darwin, BSD variants)
- New `php_version_detected` and `os_detected` fields in analysis API response
- 6 new analyzer tests for version/OS detection

### Fixed
- Case-sensitivity bug in PHPIssueAnalyzer JIT handler detection (both root cause analysis and test case generation)
- Added test coverage for lowercase JIT handler patterns

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0/),
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

### Fixed
- Case-sensitivity bug in PHPIssueAnalyzer JIT handler detection (both root cause analysis and test case generation)
- Added test coverage for lowercase JIT handler patterns

### Planned
- Full OIDC authentication implementation
- Advanced ML-based classification (optional LLM)
- Batch issue import from GitHub API
- Export to PHP test suite format (.phpt)
- Real-time analysis progress
- Comparison view for similar issues
