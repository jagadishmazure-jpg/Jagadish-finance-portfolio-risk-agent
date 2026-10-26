# How it works, step by step

## One cycle, concretely

1. **Plan.** `Agent.run_cycle` writes a `plan` ledger row, then reads
   the portfolio's exposures and thresholds through `v_exposures` and
   `v_thresholds` on the authorizer-guarded connection. Any attempt to
   read a base table directly is refused by the authorizer.
2. **Act.** Each exposure is compared with its warn/high/critical
   limits. A value at or above `warn_at` becomes a breach with a
   severity; below `warn_at` it is ignored. Before alerting, the agent
   checks `v_alert_log`: if the same (portfolio, metric, severity)
   band was alerted inside its window (default 24 hours), the alert is
   suppressed and counted in `suppressed_repeat_alerts`.
3. **Observe.** New breaches become proposals. Warning breaches are
   `proposed`; high/critical breaches are `awaiting_acknowledgement`
   until a named person acknowledges them. The summary is built with
   four sections (exposure, breach, what changed, suggested next step),
   ledger rows for `observe` and `summary` are appended, and the
   exposure values are remembered so the next cycle can report change.
4. **Repeat.** The next cycle re-reads everything. A changed value
   appears as `60.0 -> 62.0` under "what changed"; once a window
   expires, a still-breaching metric alerts again.

## Worked example (synthetic seed)

Portfolio `KAV-GROWTH` has a 60% single-sector concentration against
limits of warn 50 / high 55 / critical 65, so cycle 1 reports a HIGH
breach and requires acknowledgement. A second immediate cycle reports
no new proposals — deduplication, proven by
`test_breach_dedup_no_repeat_alert_same_window`. Backdating the alert
log past the window makes the breach alert again, proven by
`test_breach_repeats_after_window_expires`.
