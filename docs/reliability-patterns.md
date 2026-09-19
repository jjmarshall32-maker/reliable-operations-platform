# Reliability Patterns

## 1. Durable run ledger

Persist run and step state outside the process. If the process disappears, the next operator or process should not have to infer what happened from memory.

## 2. Close abandoned `running` state

A hard interruption may bypass cleanup handlers. On startup, identify old `running` records beyond an allowed age and mark them interrupted/failed before beginning new work.

## 3. Idempotent input identity

Assign a logical input identity independent of transient file location. Enforce uniqueness in durable state. A repeated input then becomes “already accepted,” not “duplicate rows inserted.”

## 4. Recoverable versus fatal stages

Classify stages by operational dependency, not exception type. A source-specific failure may be recoverable while loss of the run ledger itself is fatal.

## 5. Explicit expected-source coverage

Maintain a registry of sources expected to participate in a run. Build health from the registry plus observed evidence so missing sources remain visible even when they produced no event.

## 6. Empty is a valid state

A structurally valid, zero-row source should be distinguishable from missing, malformed, and failed sources.

## 7. Freshness is separate from success

A collector can succeed mechanically while returning yesterday's data. A downstream refresh can succeed while serving stale data. Validate freshness explicitly.

## 8. Immutable failure evidence

Preserve rejected or malformed artifacts when policy allows. Quarantine is evidence, not trash. Recovery should be able to supersede a bad attempt without erasing that the incident occurred.

## 9. Reconcile layers

Compare expected date sets and row counts between durable layers. Do not assume “the load finished” proves that raw and typed representations are complete.

## 10. Bounded diagnostics

Integrity checks must be operationally safe. Expensive full-history validation can be separated from fast current-state checks and cached or scheduled appropriately.

## 11. UTC operational boundary

For globally scheduled workflows, choose one operational day boundary and use it consistently for run identity, same-day resume, and freshness calculations.

## 12. External dependencies fail independently

Scheduler, file delivery, browser automation, network access, database work, and downstream BI refresh all have different failure modes. Model them as boundaries rather than one indivisible “daily job.”
