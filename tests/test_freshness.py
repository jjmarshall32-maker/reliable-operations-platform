from datetime import datetime, timedelta, timezone

from reliable_ops.freshness import FreshnessPolicy, evaluate_freshness
from reliable_ops.models import FreshnessStatus


def test_freshness_transitions_are_explicit():
    now = datetime(2030, 1, 1, 12, tzinfo=timezone.utc)
    policy = FreshnessPolicy(timedelta(hours=6), timedelta(hours=12))

    assert evaluate_freshness(now - timedelta(hours=1), now, policy) == FreshnessStatus.FRESH
    assert evaluate_freshness(now - timedelta(hours=8), now, policy) == FreshnessStatus.WARNING
    assert evaluate_freshness(now - timedelta(hours=14), now, policy) == FreshnessStatus.STALE
