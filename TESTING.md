# Testing

From an activated environment, run:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m py_compile extract_strings.py extract_endpoints.py find_endpoints.py find_config.py
python extract_strings.py --help
```

Runtime packages are declared in `requirements.txt`; test tooling is declared in `requirements-dev.txt`. On 2026-09-20 the complete suite, including mocked PlayFab contract tests, passed: **40 tests**.

API tests should use a temporary SQLite database and an in-process FastAPI client. Test isolation must not depend on a developer's `.env` or database. Minimum coverage includes startup, health/status, registration validation and duplicate rejection, login success and uniform invalid-credential responses, token expiry/revocation, authorization, persistence constraints, response secrecy, and generated OpenAPI routes. Gameplay simulations should cover ownership checks and invalid state transitions.

Scanner tests should use small synthetic byte fixtures and cover chunk boundaries, deduplication, invalid paths, invalid limits, valid/invalid IP ports, result caps, and config preview truncation.

No passing local unit test establishes compatibility with a proprietary client or hosted service. Such a claim would require a separately authorized interoperability plan and reproducible evidence.
