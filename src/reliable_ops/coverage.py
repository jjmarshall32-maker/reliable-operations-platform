from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .models import CoverageStatus


@dataclass(frozen=True)
class ExpectedSource:
    source_id: str
    required: bool = True


def classify_coverage(
    expected: Iterable[ExpectedSource], observed: Mapping[str, CoverageStatus]
) -> dict[str, CoverageStatus]:
    """Keep expected sources visible even when no event was observed."""
    result = {item.source_id: observed.get(item.source_id, CoverageStatus.MISSING) for item in expected}
    # Newly observed sources are not hidden; callers can flag them for registry review.
    for source_id, status in observed.items():
        result.setdefault(source_id, status)
    return result
