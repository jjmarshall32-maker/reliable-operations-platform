from reliable_ops.models import RunStatus, StepStatus
from reliable_ops.pipeline import PipelineRunner, Step
from reliable_ops.store import OperationsStore


def test_successful_steps_are_skipped_when_same_run_resumes(tmp_path):
    store = OperationsStore(tmp_path / "ops.sqlite")
    calls = []

    runner = PipelineRunner(store)
    assert runner.run(
        "run-1",
        [
            Step("collect", lambda: calls.append("collect")),
            Step("stage", lambda: calls.append("stage")),
        ],
    ) == RunStatus.SUCCESS

    assert runner.run(
        "run-1",
        [
            Step("collect", lambda: calls.append("collect-again")),
            Step("stage", lambda: calls.append("stage-again")),
        ],
    ) == RunStatus.SUCCESS

    assert calls == ["collect", "stage"]


def test_recoverable_failure_allows_independent_later_stage(tmp_path):
    store = OperationsStore(tmp_path / "ops.sqlite")
    calls = []

    def fail():
        calls.append("optional-source")
        raise RuntimeError("synthetic source failure")

    result = PipelineRunner(store).run(
        "run-warning",
        [
            Step("optional-source", fail, recoverable=True),
            Step("publish-independent", lambda: calls.append("publish")),
        ],
    )

    assert result == RunStatus.WARNING
    assert calls == ["optional-source", "publish"]
    assert store.step_statuses("run-warning") == {
        "optional-source": StepStatus.FAILED,
        "publish-independent": StepStatus.SUCCESS,
    }


def test_fatal_failure_stops_downstream_work(tmp_path):
    store = OperationsStore(tmp_path / "ops.sqlite")
    calls = []

    def fail():
        calls.append("critical")
        raise RuntimeError("synthetic critical failure")

    result = PipelineRunner(store).run(
        "run-failed",
        [
            Step("critical", fail, recoverable=False),
            Step("never-run", lambda: calls.append("never")),
        ],
    )

    assert result == RunStatus.FAILED
    assert calls == ["critical"]
