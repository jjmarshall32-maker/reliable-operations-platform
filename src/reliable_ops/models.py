from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class RunStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    FAILED = "failed"


class StepStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class CoverageStatus(StrEnum):
    LOADED = "loaded"
    EMPTY = "empty"
    MISSING = "missing"
    MALFORMED = "malformed"
    FAILED = "failed"


class FreshnessStatus(StrEnum):
    FRESH = "fresh"
    WARNING = "warning"
    STALE = "stale"


@dataclass(frozen=True)
class SourceEvent:
    run_id: str
    source_id: str
    status: CoverageStatus
    detail: str = ""
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
