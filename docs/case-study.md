# Case Study: Modernizing a Fragile Reporting Workflow

## Context

The original problem was not “build another dashboard.” The larger problem was a business-critical reporting path assembled from scheduled source delivery, file movement, formatting, database loads, transformations, and downstream refreshes.

As that workflow grew, operational risk grew with it. Failures were no longer binary. A run might partially succeed. One source might be absent while others were valid. A rerun might fix the missing source but duplicate previously loaded data. A downstream refresh might complete even though a required source was old.

I approached the problem as a reliability and data-platform redesign.

This public case study describes only transferable engineering concepts. The implementation in this repository was written from scratch for demonstration.

## Failure modes I designed around

### Late or missing sources

A scheduler reporting “success” does not prove the data is current. Freshness is therefore a first-class contract rather than an inferred property.

### Empty versus failed inputs

An expected source can legitimately contain zero rows. That is different from a missing file, malformed payload, or failed acquisition. Collapsing these states makes operations ambiguous.

### Partial success

Independent work should not be thrown away because one source fails. The orchestration model preserves completed steps and allows recoverable problems to produce a warning state while later independent work continues.

### Interrupted runs

Processes can die outside ordinary exception handling: host restart, process termination, network loss, or scheduler interruption. Durable step state allows the next run to identify prior work and resume safely.

### Duplicate ingestion

Operators need to be able to rerun with confidence. Stable logical input identities and uniqueness constraints make “already accepted” a normal state instead of a duplicate-data incident.

### Historical scale versus dashboard responsiveness

Durable history and interactive reporting have different performance requirements. The architecture keeps those concerns separate: history is preserved, while reporting models can be shaped and bounded for their consumers.

## Architectural response

I decomposed the workflow into explicit responsibilities:

1. collect or receive source artifacts
2. preserve raw evidence
3. normalize and validate
4. load typed staging structures
5. validate required-source freshness
6. refresh durable historical models
7. build reporting-serving models
8. trigger downstream publication
9. record structured operational facts throughout

The important change is not the number of stages. It is that each stage has a clear contract, durable evidence, and defined recovery behavior.

## Control-plane thinking

Once a pipeline matters operationally, it needs a control plane separate from its business data.

The public demonstration includes a small version of that idea:

- pipeline run ledger
- per-step status
- accepted-input registry
- source outcomes
- coverage classification
- freshness policy evaluation
- integrity reconciliation

This lets an operator answer “what happened?” without parsing application logs from scratch.

## Testing strategy

Waiting for the next scheduled run is a poor debugging loop. I favor isolated replay with known inputs and explicit qualification of restart behavior.

A representative acceptance sequence is:

1. load a controlled synthetic input set
2. execute the pipeline
3. rerun the same logical inputs
4. confirm no duplicate ingestion
5. inject a recoverable source problem
6. verify independent stages still execute
7. simulate an interrupted run
8. verify stale running state is closed and safe resume works
9. compare layer counts for integrity regressions

The tests in this repository exercise those contracts directly.

## What this project demonstrates about my work

My contribution to this class of system spans more than report authoring:

- Python automation and orchestration
- relational operational-state modeling
- ETL/ELT boundary design
- idempotency and restart safety
- data-quality and freshness controls
- structured telemetry and health modeling
- safe test/replay environments
- historical-versus-serving data architecture
- operational documentation and Git-based change discipline

The goal is not clever code. The goal is a system that can be understood, operated, recovered, and extended under imperfect real-world conditions.
