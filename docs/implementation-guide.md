# Implementation guide (for adopters)

## Adopting the loop

1. Copy `src/portfolio_risk_agent` into your project (standard
   library only; no third-party dependency to audit).
2. Replace `seed.py` with your own loader. Keep the view layer:
   expose only the views your agent may read, and keep the authorizer
   in front of every read connection.
3. Keep the write surface narrow: the only writes in this design are
   ledger and alert-log appends with allow-listed steps and
   parameterised queries. Do not hand the agent a general write
   connection "for convenience" — that single decision removes most
   of the guardrails in `docs/guardrails.md`.
4. Re-tune thresholds per portfolio and per metric, and re-run the
   suite after every change to the authorizer or gate logic. The
   authorizer tests must keep running with the text check disabled;
   if they ever need the text check to pass, the authorizer itself has
   regressed.

## Extending safely

- New metrics: add a threshold row and a severity expectation test
  before wiring the metric into any summary.
- New channels: default to dry-run, require explicit opt-in, refuse in
  CI, and redact before sending — the pattern in `notify.py`.
- New approval scopes: one scope string per action, exact match only;
  never widen a scope to "all" to save effort.
- Persistence: when moving approvals/acknowledgements out of memory,
  keep single-use (mark consumed in the same transaction as the
  gated action) and keep expiry enforced at validation time, not at
  issuance time only.

## What not to copy blindly

- The seed values and limits are illustrative, not recommended risk
  policy. Set limits with your risk function, not from this demo.
- The 100-row cap suits a demo; size it to your portfolios and test
  the truncation path, not just the happy path.
