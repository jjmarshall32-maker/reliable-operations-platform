from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .models import RunStatus, StepStatus
from .store import OperationsStore


@dataclass(frozen=True)
class Step:
    name: str
    action: Callable[[], None]
    recoverable: bool = True


class PipelineRunner:
    def __init__(self, store: OperationsStore):
        self.store = store

    def run(self, run_id: str, steps: Iterable[Step]) -> RunStatus:
        self.store.begin_run(run_id)
        already_complete = self.store.successful_steps(run_id)
        had_warning = False

        for step in steps:
            if step.name in already_complete:
                continue

            self.store.start_step(run_id, step.name)
            try:
                step.action()
            except Exception as exc:
                detail = f"{type(exc).__name__}: {exc}"
                self.store.finish_step(run_id, step.name, StepStatus.FAILED, detail)
                if step.recoverable:
                    had_warning = True
                    continue
                self.store.finish_run(run_id, RunStatus.FAILED, detail)
                return RunStatus.FAILED
            else:
                self.store.finish_step(run_id, step.name, StepStatus.SUCCESS)

        final = RunStatus.WARNING if had_warning else RunStatus.SUCCESS
        self.store.finish_run(run_id, final)
        return final
