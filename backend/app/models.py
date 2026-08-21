"""
MVP note: runs are held in-memory keyed by run_id for simplicity during the
sprint. Swap RUN_STORE for real Supabase Postgres persistence (runs /
run_results tables) once the core flow works end to end.
"""
from typing import Any

RUN_STORE: dict[str, dict[str, Any]] = {}
