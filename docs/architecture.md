# Architecture

## System boundaries

### 1. Collection boundary

Collectors are treated as unreliable integrations. They may return valid data, valid emptiness, malformed content, or no result at all.

The platform records those outcomes explicitly instead of representing every non-download as a generic exception.

### 2. Raw evidence boundary

Accepted source artifacts should be preserved before destructive transformation. Raw evidence makes later reconciliation, replay, and investigation possible.

A production implementation would normally use durable object/file storage plus metadata that links an artifact to a run and source attempt.

### 3. Normalization boundary

Formatting converts source-shaped data into stable internal contracts. Structural drift is validated deliberately; unsupported fields should not silently change the meaning of existing columns.

### 4. Typed staging boundary

Typed staging is where parsing and normalization become queryable relational facts. Invalid rows should be isolated or reported rather than silently dropped.

### 5. History boundary

Durable historical structures preserve the long-lived record. Retention here is a data-governance decision, not a dashboard-performance shortcut.

### 6. Reporting boundary

Reporting models are consumer-oriented. They can be denormalized, pre-aggregated, or time-bounded without weakening the historical system of record.

### 7. Operations control plane

Operational data answers questions the business tables should not have to answer:

- when a run started and ended
- which step is running
- which steps succeeded
- which sources were loaded, empty, missing, malformed, or failed
- what inputs have already been accepted
- whether required data is fresh
- whether layer counts still reconcile

## Durable-state model

The demo uses SQLite tables for:

- `pipeline_runs`
- `step_runs`
- `accepted_inputs`
- `source_events`

In a larger deployment these records can live in PostgreSQL and support API or dashboard views.

## Restart behavior

A restart-safe stage must satisfy at least one of these conditions:

- naturally idempotent operation
- unique logical input key
- replace/rebuild semantics
- durable completion marker
- reconciliation capable of proving the desired state already exists

The demo runner stores successful step state. When the same run identifier is resumed, successful stages are skipped and unsuccessful stages can be attempted again.

## Warning versus failure

A recoverable stage exception records a failed step but promotes the overall run to `warning`, allowing later independent stages to execute. A fatal stage exception stops downstream work and marks the run `failed`.

That distinction is important: not every technical exception has the same operational impact.

## Freshness contract

Freshness is evaluated independently of process completion:

```text
latest accepted data timestamp
        + source freshness policy
        + current UTC time
        = fresh | warning | stale
```

## Coverage contract

Expected-source coverage uses explicit states:

```text
loaded | empty | missing | malformed | failed
```

This avoids treating “zero records” as equivalent to “we never received anything.”
