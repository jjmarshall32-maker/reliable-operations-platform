# Testing and Replay

## Goal

A production incident should be reproducible without modifying production state.

## Recommended isolated workflow

1. Copy only approved, non-sensitive fixtures into an isolated test area.
2. Use separate database/storage configuration.
3. Run the same orchestration code shape where practical.
4. Replace external publication with a harmless stub or test endpoint.
5. Preserve test run/step events for inspection.

## Restart qualification

Idempotency claims should be proven, not assumed.

A useful qualification sequence is:

```text
controlled inputs
    -> run A
    -> capture counts/state
    -> run A again
    -> verify no duplicate logical inputs
    -> interrupt a run mid-stage
    -> recover stale run state
    -> resume
    -> verify terminal state and reconciled counts
```

## Failure injection

The tests intentionally exercise:

- already-completed step skip
- recoverable step failure with later continuation
- fatal step failure with downstream stop
- duplicate logical input rejection
- stale-running recovery
- expected-source coverage states
- freshness transitions
- raw/staging count mismatch detection

## Why this matters

The operator experience during failure is part of system quality. A good test suite validates not only transformations but also what the system says happened and what a safe rerun will do next.
