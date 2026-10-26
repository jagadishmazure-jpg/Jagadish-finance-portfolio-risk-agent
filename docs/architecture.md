# Architecture

```mermaid
flowchart TD
    subgraph Agent["Agent loop (plan -> act -> observe -> repeat)"]
        P[Plan: read exposures + thresholds]
        A[Act: detect breaches, deduplicate]
        O[Observe: ledger rows + summary]
        P --> A --> O --> P
    end
    subgraph Store["SQLite store"]
        T1[(positions)]
        T2[(exposures)]
        T3[(thresholds)]
        T4[(run_ledger)]
        T5[(alert_log)]
    end
    subgraph Views["Allowed views (only readable path)"]
        V1[v_positions]
        V2[v_exposures]
        V3[v_thresholds]
        V4[v_run_ledger]
        V5[v_alert_log]
    end
    P -->|guarded read connection| Views
    Views --> Store
    A -->|append only, allow-listed steps| T4
    A -->|append only| T5
    O --> S[Structured summary]
    S --> H[Human checkpoint]
    H -->|named-person acknowledgement| S
    S -.->|never| X[Trade execution: does not exist]
```

## Component map

| Component | File | Job |
|---|---|---|
| Guarded access + row cap + ledger appends | `src/portfolio_risk_agent/db.py` | Authorizer, views, `fetchmany` cap, the only write path |
| Synthetic seed | `src/portfolio_risk_agent/seed.py` | Invented positions, exposures, thresholds |
| Readers | `src/portfolio_risk_agent/readers.py` | View-only queries, no rewritten query text |
| Thresholds + dedup | `src/portfolio_risk_agent/thresholds.py` | Severity tiers, breach detection, window logic |
| Approvals + gates | `src/portfolio_risk_agent/approvals.py` | Named-person, single-use, scoped, expiring approvals; consent parsing |
| Redaction | `src/portfolio_risk_agent/redaction.py` | Card, email, phone, SSN masking |
| Summaries | `src/portfolio_risk_agent/summaries.py` | Four-section briefs, `trade_executed: false` |
| Costs | `src/portfolio_risk_agent/costs.py` | Negative-rejecting budget arithmetic |
| Notify | `src/portfolio_risk_agent/notify.py` | Dry-run-by-default email channel |
| Brand guard | `src/portfolio_risk_agent/brand.py` | Hash-only blocklist |
| Agent | `src/portfolio_risk_agent/agent.py` | The plan/act/observe/repeat loop |
