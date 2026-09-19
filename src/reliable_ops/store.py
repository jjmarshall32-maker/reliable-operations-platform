from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .models import CoverageStatus, RunStatus, StepStatus


def _iso(value: datetime | None = None) -> str:
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


class OperationsStore:
    """Small durable control-plane store used by the public demo."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.initialize()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS step_runs (
                    run_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (run_id, step_name)
                );

                CREATE TABLE IF NOT EXISTS accepted_inputs (
                    logical_input_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    accepted_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS source_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT '',
                    occurred_at TEXT NOT NULL
                );
                """
            )

    def begin_run(self, run_id: str, *, now: datetime | None = None) -> None:
        timestamp = _iso(now)
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT status FROM pipeline_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO pipeline_runs(run_id, started_at, status) VALUES (?, ?, ?)",
                    (run_id, timestamp, RunStatus.RUNNING.value),
                )
            elif existing["status"] != RunStatus.SUCCESS.value:
                conn.execute(
                    "UPDATE pipeline_runs SET status = ?, ended_at = NULL WHERE run_id = ?",
                    (RunStatus.RUNNING.value, run_id),
                )

    def finish_run(
        self, run_id: str, status: RunStatus, detail: str = "", *, now: datetime | None = None
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE pipeline_runs SET status = ?, detail = ?, ended_at = ? WHERE run_id = ?",
                (status.value, detail, _iso(now), run_id),
            )

    def run_status(self, run_id: str) -> RunStatus | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT status FROM pipeline_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return RunStatus(row["status"]) if row else None

    def start_step(self, run_id: str, step_name: str, *, now: datetime | None = None) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO step_runs(run_id, step_name, started_at, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(run_id, step_name) DO UPDATE SET
                    started_at = excluded.started_at,
                    ended_at = NULL,
                    status = excluded.status,
                    detail = ''
                """,
                (run_id, step_name, _iso(now), StepStatus.RUNNING.value),
            )

    def finish_step(
        self,
        run_id: str,
        step_name: str,
        status: StepStatus,
        detail: str = "",
        *,
        now: datetime | None = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE step_runs
                SET ended_at = ?, status = ?, detail = ?
                WHERE run_id = ? AND step_name = ?
                """,
                (_iso(now), status.value, detail, run_id, step_name),
            )

    def successful_steps(self, run_id: str) -> set[str]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT step_name FROM step_runs WHERE run_id = ? AND status = ?",
                (run_id, StepStatus.SUCCESS.value),
            ).fetchall()
        return {row["step_name"] for row in rows}

    def step_statuses(self, run_id: str) -> dict[str, StepStatus]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT step_name, status FROM step_runs WHERE run_id = ?", (run_id,)
            ).fetchall()
        return {row["step_name"]: StepStatus(row["status"]) for row in rows}

    def register_input(
        self, logical_input_id: str, run_id: str, *, now: datetime | None = None
    ) -> bool:
        """Return True only when this logical input is accepted for the first time."""
        try:
            with self.connect() as conn:
                conn.execute(
                    "INSERT INTO accepted_inputs(logical_input_id, run_id, accepted_at) VALUES (?, ?, ?)",
                    (logical_input_id, run_id, _iso(now)),
                )
        except sqlite3.IntegrityError:
            return False
        return True

    def record_source_event(
        self,
        run_id: str,
        source_id: str,
        status: CoverageStatus,
        detail: str = "",
        *,
        now: datetime | None = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO source_events(run_id, source_id, status, detail, occurred_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, source_id, status.value, detail, _iso(now)),
            )

    def latest_source_statuses(self, run_id: str) -> dict[str, CoverageStatus]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT se.source_id, se.status
                FROM source_events se
                JOIN (
                    SELECT source_id, MAX(id) AS max_id
                    FROM source_events
                    WHERE run_id = ?
                    GROUP BY source_id
                ) latest ON latest.max_id = se.id
                """,
                (run_id,),
            ).fetchall()
        return {row["source_id"]: CoverageStatus(row["status"]) for row in rows}

    def recover_stale_runs(self, started_before: datetime) -> list[str]:
        if started_before.tzinfo is None:
            raise ValueError("started_before must be timezone-aware")
        cutoff = _iso(started_before)
        recovered: list[str] = []
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT run_id FROM pipeline_runs WHERE status = ? AND started_at < ?",
                (RunStatus.RUNNING.value, cutoff),
            ).fetchall()
            recovered = [row["run_id"] for row in rows]
            for run_id in recovered:
                conn.execute(
                    """
                    UPDATE pipeline_runs
                    SET status = ?, ended_at = ?, detail = ?
                    WHERE run_id = ?
                    """,
                    (
                        RunStatus.FAILED.value,
                        _iso(),
                        "Recovered abandoned running state after interruption.",
                        run_id,
                    ),
                )
                conn.execute(
                    """
                    UPDATE step_runs
                    SET status = ?, ended_at = ?, detail = ?
                    WHERE run_id = ? AND status = ?
                    """,
                    (
                        StepStatus.FAILED.value,
                        _iso(),
                        "Interrupted before normal finalization.",
                        run_id,
                        StepStatus.RUNNING.value,
                    ),
                )
        return recovered
