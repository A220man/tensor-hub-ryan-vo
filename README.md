# PHP Issue Analyzer

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


**Ryan Vo | AI & Machine Learning**

A developer tool for analyzing PHP interpreter issues from GitHub, classifying them automatically, and generating reproducible test cases.

## Problem

PHP interpreter bugs (segfaults, performance regressions, logic errors) are reported on GitHub with varying quality. Developers spend significant time manually classifying issues, extracting stack traces, and writing reproduction scripts. This tool automates that workflow using deterministic pattern matching—no LLM required.

## Approach

- **Rule-based classification** — 7 categories (segfault, performance, memory, logic_bug, platform_specific, feature_request, unknown) using keyword/regex patterns derived from real PHP-src issues
- **Structured extraction** — Stack traces, error patterns, PHP versions, OS metadata parsed from issue bodies
- **Root cause analysis** — Pattern-matched explanations with confidence scores and suggested fixes
- **Test case generation** — Ready-to-run PHP scripts for known issue types (JIT segfaults, array_unique bugs, macOS fork crashes, GC performance, ldap shutdown crashes, enum array keys)

## Intended User

PHP core developers, extension authors, and QA engineers who triage PHP-src issues and need reproducible test cases quickly.

---

## Quick Start

### Prerequisites
- Docker 24+ and Docker Compose v2
- Or: Python 3.12 + Node 24 for local development

### Docker (Recommended)
```bash
# Clone and configure
git clone https://github.com/A220man/tensor-hub-ryan-vo
cd tensor-hub-ryan-vo
cp .env.example .env

# Start all services (backend, frontend, Keycloak)
docker compose up --build -d

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Keycloak: http://localhost:8080 (admin/admin)
```

### Local Development
```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Run tests
# Backend:
source .venv/bin/activate && pytest backend/tests -v
# Frontend:
cd frontend && npm test
```

---

## Architecture

```mermaid
flowchart LR
    subgraph Client
        UI[React Dashboard]
    end
    subgraph API[FastAPI Backend]
        Issues[/api/issues]
        Analyze[/api/issues/analyze]
        Health[/api/health]
    end
    subgraph Engine
        Classifier[PHPIssueAnalyzer]
        Patterns[Pattern Library]
    end
    subgraph Storage
        SQLite[(SQLite)]
    end
    subgraph Auth
        KC[Keycloak OIDC]
    end

    UI --> Issues
    UI --> Analyze
    Issues --> Classifier
    Analyze --> Classifier
    Classifier --> Patterns
    Classifier --> SQLite
    Issues --> SQLite
    UI -.-> KC
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/issues` | Create issue with auto-analysis |
| POST | `/api/issues/analyze` | Analyze issue text without persisting |
| GET | `/api/issues` | List issues (pagination, filters) |
| GET | `/api/issues/{id}` | Get issue with analysis |
| PATCH | `/api/issues/{id}` | Update issue |
| POST | `/api/issues/{id}/reanalyze` | Re-run analysis |
| DELETE | `/api/issues/{id}` | Delete issue |

### Example: Analyze an Issue
```bash
curl -X POST http://localhost:8000/api/issues/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "array_unique() with SORT_REGULAR returns duplicates",
    "body": "PHP 8.4.13: array_unique([\"5\", \"10\", \"5\", \"3A\", \"5\"], SORT_REGULAR) returns 4 elements instead of 3",
    "php_version": "8.4.13",
    "os": "Linux"
  }'
```

Response:
```json
{
  "issue": { "id": 1, "title": "...", "category": "logic_bug", ... },
  "analysis": {
    "classification": "logic_bug",
    "confidence": 95,
    "root_cause": "SORT_REGULAR uses zendi_smart_strcmp which has non-transitive comparison...",
    "suggested_fix": "Use SORT_STRING for string arrays..."
  },
  "test_case": {
    "code": "<?php\n$units = ['5', '10', '5', '3A', '5', '5'];\n$unique = array_unique($units, SORT_REGULAR);\n...",
    "expected_behavior": "Returns 3 unique values: 5, 10, 3A"
  }
}
```

---

## Supported Issue Patterns

| Category | Patterns Detected | Example Issues |
|----------|-------------------|----------------|
| **segfault** | `segmentation fault`, `SIGSEGV`, `ZEND_*_HANDLER`, `CACHED_PTR`, `ldap_bind` + `ENGINE_cleanup` | #7817, #8620, #10430 |
| **performance** | `GC_THRESHOLD`, `slowdown`, `regression`, `benchmark` | #9993 |
| **memory** | `memory leak`, `OOM`, `allocation` | — |
| **logic_bug** | `array_unique` + `SORT_REGULAR`, `enum` + `array`, `transitive`, `duplicate` | #20262, #9208 |
| **platform_specific** | `macos`, `darwin`, `objc`, `fork`, `__NSPlaceholderDate` | #11818 |
| **feature_request** | `feature request`, `can this be implemented`, `RFC` | #9208 |
| **unknown** | No pattern match | — |

---

## AI/ML Evaluation

This tool uses **deterministic rule-based classification**—no LLM required for core functionality. The classifier achieves high accuracy on the 7 reference issues from php/php-src:

| Issue | Category | Confidence | Test Case Generated |
|-------|----------|------------|---------------------|
| #7817 JIT segfault | segfault | 85% | ✅ |
| #9208 Enum array key | feature_request | 40% | ✅ (workaround) |
| #9993 GC performance | performance | 75% | ✅ |
| #11818 macOS fork crash | platform_specific | 90% | ✅ |
| #20262 array_unique bug | logic_bug | 95% | ✅ |
| #10430 print_r heisenbug | segfault | 60% | ❌ (generic) |
| #8620 ldap shutdown crash | segfault | 80% | ✅ |

**Reproducible command:**
```bash
source .venv/bin/activate && python -c "
from backend.app.services.analyzer import PHPIssueAnalyzer
from backend.app.models.schemas import AnalyzeRequest

analyzer = PHPIssueAnalyzer()
issues = [
    ('JIT segfault', 'PHP 8.1.0 segfault in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER CACHED_PTR'),
    ('GC perf', 'GC_THRESHOLD performance regression between 8.1.9 and 8.1.10'),
    ('array_unique', 'array_unique SORT_REGULAR returns duplicates with 5 10 3A'),
]
for title, body in issues:
    analysis, tc = analyzer.analyze(AnalyzeRequest(title=title, body=body))
    print(f'{title}: {analysis.classification} ({analysis.confidence}%)')
"
```

**Limitations:**
- No semantic understanding—relies on keyword/regex matching
- Confidence scores are heuristic, not calibrated probabilities
- Generic/unknown issues produce template test cases only
- LLM enhancement (optional) not yet implemented

---

## Security Limitations

- **Demo mode**: OIDC disabled by default; no authentication in local development
- **Production**: Enable OIDC with Keycloak, set `SECRET_KEY`, use HTTPS behind TLS reverse proxy
- **No secrets in repo**: All credentials via environment variables
- **SQLite**: Local development only; use PostgreSQL for production

---

## Provider Configuration

| Provider | LLM_PROVIDER | LLM_MODEL | LLM_BASE_URL |
|----------|--------------|-----------|--------------|
| OpenAI | `openai` | `gpt-4o` | `https://api.openai.com/v1` |
| Anthropic | `anthropic` | `claude-3-5-sonnet` | `https://api.anthropic.com` |
| Gemini | `gemini` | `gemini-1.5-pro` | `https://generativelanguage.googleapis.com` |
| Ollama | `ollama` | `llama3.1` | `http://localhost:11434/v1` |
| OpenRouter | `openai` | `openrouter/auto` | `https://openrouter.ai/api/v1` |
| LiteLLM | `openai` | `*` | `http://localhost:4000` |

Set `LLM_API_KEY` and `LLM_PROVIDER` to enable optional LLM-enhanced test case generation.

---

## SSO/SAML Setup

Keycloak supports SAML 2.0 identity brokering:

1. In Keycloak Admin Console: **Identity Providers → Add Provider → SAML v2.0**
2. Configure IdP metadata (entity ID, SSO URL, certificates)
3. Map SAML attributes to Keycloak user attributes
4. Enable **First Login Flow** for user registration

No native SAML implementation in this application—Keycloak handles the broker.

---

## Backup & Restore

```bash
# Backup SQLite
docker compose exec backend cp /app/data/tensor_hub.db /app/data/backup_$(date +%F).db

# Restore
docker compose exec backend cp /app/data/backup_2024-10-22.db /app/data/tensor_hub.db
```

---

## License

MIT © Ryan Vo <ryandtvo@gmail.com>