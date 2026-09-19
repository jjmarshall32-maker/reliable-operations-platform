from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import FreshnessStatus


@dataclass(frozen=True)
class FreshnessPolicy:
    warning_after: timedelta
    stale_after: timedelta

    def __post_init__(self) -> None:
        if self.warning_after < timedelta(0):
            raise ValueError("warning_after must be non-negative")
        if self.stale_after <= self.warning_after:
            raise ValueError("stale_after must be greater than warning_after")


def evaluate_freshness(
    latest_data_at: datetime, now: datetime, policy: FreshnessPolicy
) -> FreshnessStatus:
    if latest_data_at.tzinfo is None or now.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")

    age = now - latest_data_at
    if age >= policy.stale_after:
        return FreshnessStatus.STALE
    if age >= policy.warning_after:
        return FreshnessStatus.WARNING
    return FreshnessStatus.FRESH
