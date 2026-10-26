# Limitations and known failures

Kept visible on purpose. Each item below is a real boundary of this
scaffold, not a footnote to be discovered later.

- **Synthetic data only.** One portfolio, four exposures, invented
  values. Nothing here validates against real market data, and no
  accuracy claim is made: the suite is 59 regression checks, not a
  quality benchmark.
- **No live feed.** Exposures change only when a test or operator
  edits the store. A production watcher would need an ingestion path
  with its own validation; that path does not exist here.
- **Dedup durability.** Windows live in the alert log. Delete the
  database file and windows reset, so the next cycle re-alerts.
  Acceptable for a demo; a production system would need a durable,
  replicated log.
- **In-memory approvals.** `ApprovalStore` lives in process memory.
  Restart the process and issued approvals are gone. Persistent,
  auditable approval storage is Planned.
- **Acknowledgements are in-process too.** Same restart caveat as
  approvals; a restart also clears the agent's previous-value memory,
  so the first post-restart cycle reports "first observation".
- **Brand hash list is exact-match only.** It catches blocked names
  written exactly, not paraphrases, misspellings, or names absent from
  the list. It is a tripwire, not a guarantee.
- **Email has no transport.** The opt-in path records to an outbox
  list; nothing actually leaves the machine. Claiming delivery would
  be false.
- **Single portfolio, single loop.** No multi-portfolio fan-out, no
  scheduler, no concurrency control. Two agents sharing one database
  file have no locking protocol in this repo.
- **Thresholds are static.** They are seeded, not learned. Drift,
  calibration, and backtesting of limits are out of scope here.
- **Known test-visible miss, by design:** cycle 2 of the demo reports
  "Breaches persist but were already alerted" rather than re-alerting.
  That is the deduplication rule, and it is the correct behaviour for
  this repo — but it means a reader skimming cycle 2 alone could think
  the portfolio is clean. Always read the exposure section, which
  still shows the breaching values.
