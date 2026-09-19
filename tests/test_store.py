from datetime import datetime, timedelta, timezone

from reliable_ops.models import RunStatus, StepStatus
from reliable_ops.store import OperationsStore


def test_logical_input_is_accepted_only_once(tmp_path):
    store = OperationsStore(tmp_path / "ops.sqlite")
    assert store.register_input("source:2030-01-01", "run-1") is True
    assert store.register_input("source:2030-01-01", "run-2") is False


def test_abandoned_running_state_can_be_recovered(tmp_path):
    store = OperationsStore(tmp_path / "ops.sqlite")
    old = datetime(2030, 1, 1, tzinfo=timezone.utc)
    store.begin_run("abandoned", now=old)
    store.start_step("abandoned", "collect", now=old)

    recovered = store.recover_stale_runs(old + timedelta(hours=1))

    assert recovered == ["abandoned"]
    assert store.run_status("abandoned") == RunStatus.FAILED
    assert store.step_statuses("abandoned")["collect"] == StepStatus.FAILED
