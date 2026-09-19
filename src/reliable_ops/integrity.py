from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping


@dataclass(frozen=True)
class DateMismatch:
    business_date: date
    raw_rows: int
    staging_rows: int


@dataclass(frozen=True)
class IntegrityResult:
    missing_in_staging: tuple[date, ...]
    missing_in_raw: tuple[date, ...]
    row_count_mismatches: tuple[DateMismatch, ...]

    @property
    def ok(self) -> bool:
        return not (self.missing_in_staging or self.missing_in_raw or self.row_count_mismatches)


def compare_layer_counts(
    raw_counts: Mapping[date, int], staging_counts: Mapping[date, int]
) -> IntegrityResult:
    raw_dates = set(raw_counts)
    staging_dates = set(staging_counts)

    common = sorted(raw_dates & staging_dates)
    mismatches = tuple(
        DateMismatch(day, raw_counts[day], staging_counts[day])
        for day in common
        if raw_counts[day] != staging_counts[day]
    )

    return IntegrityResult(
        missing_in_staging=tuple(sorted(raw_dates - staging_dates)),
        missing_in_raw=tuple(sorted(staging_dates - raw_dates)),
        row_count_mismatches=mismatches,
    )
