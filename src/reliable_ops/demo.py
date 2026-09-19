from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .archive import archive_bytes
from .coverage import ExpectedSource, classify_coverage
from .freshness import FreshnessPolicy, evaluate_freshness
from .integrity import compare_layer_counts
from .models import CoverageStatus
from .pipeline import PipelineRunner, Step
from .store import OperationsStore


def run_demo(workspace: Path) -> dict:
    workspace.mkdir(parents=True, exist_ok=True)
    store = OperationsStore(workspace / "operations.sqlite")
    run_id = "synthetic-20300101"

    expected = [
        ExpectedSource("source-a"),
        ExpectedSource("source-b"),
        ExpectedSource("source-c"),
    ]

    def collect() -> None:
        inputs = {
            "source-a": b"id,value\n1,10\n2,20\n",
            "source-b": b"id,value\n",  # valid empty source
        }
        for source_id, payload in inputs.items():
            logical_id = f"{run_id}:{source_id}"
            first_acceptance = store.register_input(logical_id, run_id)
            if not first_acceptance:
                continue
            archive_bytes(workspace / "raw", source_id, payload)
            status = CoverageStatus.EMPTY if payload.count(b"\n") <= 1 else CoverageStatus.LOADED
            store.record_source_event(run_id, source_id, status)

        # source-c demonstrates an expected source that produced malformed evidence.
        store.record_source_event(
            run_id,
            "source-c",
            CoverageStatus.MALFORMED,
            "Synthetic schema validation failure.",
        )

    def normalize() -> None:
        # A real implementation would parse raw evidence into typed staging rows.
        pass

    def publish() -> None:
        # Intentionally independent from the synthetic malformed source.
        pass

    status = PipelineRunner(store).run(
        run_id,
        [
            Step("collect", collect, recoverable=False),
            Step("normalize", normalize),
            Step("publish", publish),
        ],
    )

    coverage = classify_coverage(expected, store.latest_source_statuses(run_id))
    freshness = evaluate_freshness(
        datetime(2030, 1, 1, 6, tzinfo=timezone.utc),
        datetime(2030, 1, 1, 12, tzinfo=timezone.utc),
        FreshnessPolicy(timedelta(hours=8), timedelta(hours=16)),
    )
    integrity = compare_layer_counts(
        {date(2030, 1, 1): 2, date(2030, 1, 2): 3},
        {date(2030, 1, 1): 2, date(2030, 1, 2): 3},
    )

    return {
        "run_status": status.value,
        "coverage": {key: value.value for key, value in coverage.items()},
        "freshness": freshness.value,
        "integrity_ok": integrity.ok,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the clean-room reliability demo.")
    parser.add_argument("--workspace", type=Path, default=Path(".demo"))
    args = parser.parse_args()
    print(json.dumps(run_demo(args.workspace), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
