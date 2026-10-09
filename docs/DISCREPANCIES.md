# FraudMesh discrepancies

## D-001 — Persistence implementation uses stdlib `sqlite3`

- **Source expectation:** The technical documentation names SQLAlchemy for the SQLite persistence layer.
- **Implemented behavior:** FraudMesh uses Python's standard-library `sqlite3` module behind a small repository-style database adapter.
- **Reason:** This keeps the Stage 2 synthetic loader deterministic and dependency-light while preserving SQLite/WAL semantics and the documented schema.
- **Impact:** No API contract change for the current prototype. Revisit if migrations, multi-database support, or ORM-level relationships become necessary.

