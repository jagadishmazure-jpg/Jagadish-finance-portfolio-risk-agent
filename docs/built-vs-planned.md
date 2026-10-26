# Built vs planned

## Built (tested, runnable offline)

- Agent loop: plan → act → observe → repeat, with a run ledger.
- Position/exposure readers through authorizer-guarded views.
- Threshold store with warn/high/critical tiers and ordering checks.
- Breach detection plus one-alert-per-band-per-window deduplication.
- Structured summaries: exposure, breach, what changed, suggested
  next step; `trade_executed` always false.
- Human checkpoints: proposals only; named-person acknowledgement for
  high/critical breaches.
- View-aware authorizer, confirmation gates (bypass/reject/absent/
  low-confidence/contradicting-consent), PII redaction (cards, emails,
  phones, SSNs), fetchmany row cap, negative-cost rejection,
  hash-only brand guard, dry-run email channel.
- Autonomy trade-off documentation (`docs/autonomy-tradeoffs.md`).
- Docs: all 13 checklist items, knowledge notes, scripts for overlap,
  brand, and test-count checks.

## Written, not run

Nothing in this category at release: every module listed as Built is
covered by the 59-test suite, which was run green before release.

## Planned (not claimed, not built)

- Live market-data ingestion with validation.
- Multi-portfolio support and a scheduler daemon.
- Persistent approval and acknowledgement stores with an audit trail.
- A real (credential-free by design review) notification transport.
- Threshold calibration/backtesting tooling.
- Deployment, packaging, hosted demo, badges, CI workflow files.
  (No CI configuration is shipped in this scaffold by design.)
