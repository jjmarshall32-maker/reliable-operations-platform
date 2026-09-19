# Interview Notes

## Thirty-second version

I modernized a fragile reporting workflow by treating it as an operations platform: durable orchestration state, explicit source freshness and coverage, restart-safe ingestion, structured health events, replayable tests, and separate historical versus reporting-serving models.

## Strong discussion threads

### “Tell me about a reliability problem you solved.”

Discuss why process success was insufficient, how explicit freshness/coverage changed the operational contract, and how warning versus fatal boundaries reduced unnecessary full reruns.

### “How do you make ETL safe to rerun?”

Discuss logical input identity, uniqueness constraints, deterministic transforms, durable completion state, and raw/staging reconciliation.

### “How do you debug scheduled systems?”

Discuss structured run/step/source state first, logs second; stale-running recovery; external dependency boundaries; and replay in an isolated environment.

### “How do you handle history at scale?”

Discuss the difference between durable historical truth and consumer-oriented reporting models. Preserve history; optimize serving structures independently.

### “What did you learn?”

The biggest lesson was that operational state is itself a data-modeling problem. Once the system can represent loaded, empty, missing, malformed, failed, fresh, stale, running, warning, and interrupted states explicitly, both automation and human recovery become much simpler.
