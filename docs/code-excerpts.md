# Real code excerpts and their real output

## Excerpt 1: running one agent cycle

```python
from portfolio_risk_agent.db import connect_admin, connect_read, create_schema
from portfolio_risk_agent.seed import seed
from portfolio_risk_agent.agent import Agent

admin = connect_admin("demo.db")
create_schema(admin)
seed(admin)
agent = Agent(connect_read("demo.db"), admin)
summary = agent.run_cycle("demo-run-1")
```

## Real output (cycle 1 of the demo, synthetic data, 4 exposures)

```json
{
  "breach": [
    "HIGH breach: single_sector_pct = 60.0 (warn 50.0, high 55.0, critical 65.0)",
    "WARNING breach: equity_weight_pct = 60.0 (warn 55.0, high 65.0, critical 75.0)",
    "HIGH breach: top_holding_pct = 42.0 (warn 30.0, high 40.0, critical 50.0)"
  ],
  "exposure": [
    "single_sector_pct: 60.0 (as of 2026-10-26)",
    "equity_weight_pct: 60.0 (as of 2026-10-26)",
    "top_holding_pct: 42.0 (as of 2026-10-26)",
    "liquidity_days: 4.0 (as of 2026-10-26)"
  ],
  "portfolio_id": "KAV-GROWTH",
  "proposals": [
    {
      "acknowledged_by": null,
      "metric": "single_sector_pct",
      "proposal_id": "demo-run-1:single_sector_pct:high",
      "severity": "high",
      "status": "awaiting_acknowledgement",
      "suggested_action": "PROPOSED review of the breaching exposure by the risk owner"
    },
    {
      "acknowledged_by": null,
      "metric": "equity_weight_pct",
      "proposal_id": "demo-run-1:equity_weight_pct:warning",
      "severity": "warning",
      "status": "proposed",
      "suggested_action": "PROPOSED review of the breaching exposure by the risk owner"
    },
    {
      "acknowledged_by": null,
      "metric": "top_holding_pct",
      "proposal_id": "demo-run-1:top_holding_pct:high",
      "severity": "high",
      "status": "awaiting_acknowledgement",
      "suggested_action": "PROPOSED review of the breaching exposure by the risk owner"
    }
  ],
  "requires_acknowledgement": true,
  "run_id": "demo-run-1",
  "suggested_next_step": "Seek named-person acknowledgement, then review the position with the risk owner.",
  "suppressed_repeat_alerts": 0,
  "trade_executed": false,
  "unacknowledged_high_breaches": [
    "KAV-GROWTH:single_sector_pct:high",
    "KAV-GROWTH:top_holding_pct:high"
  ],
  "what_changed": [
    "single_sector_pct: first observation in this ledger",
    "equity_weight_pct: first observation in this ledger",
    "top_holding_pct: first observation in this ledger"
  ]
}
```

## What cycle 2 shows

Running a second cycle immediately after the first produces no new
proposals: the same breach bands were already alerted inside their
24-hour window, so the agent suppresses repeats and reports
`"suppressed_repeat_alerts": 3` with the note that the breaches persist
but were already alerted. That is the deduplication rule working, not a
missing detection -- the exposures are still listed in the summary.

## Excerpt 2: the guarded read

```python
from portfolio_risk_agent.db import connect_read, run_view_query

con = connect_read("demo.db")  # authorizer-guarded, view-only
rows, truncated = run_view_query(
    con, "SELECT metric, value FROM v_exposures WHERE portfolio_id = ?", ("KAV-GROWTH",))
```

A direct `SELECT * FROM positions` on this connection is refused by the
SQLite authorizer itself ("access to positions.portfolio_id is
prohibited"), as proven in `tests/test_authorizer.py` with the text
pre-check switched off.
