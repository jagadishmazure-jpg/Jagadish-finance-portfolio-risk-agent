# Interview points

Use these as talking points, each backed by a test you can open.

1. **"The agent cannot trade, by construction."** There is no
   execution method in the package; proposals are records. Point to
   `test_agent_never_executes_trades` and to the `trade_executed:
   false` field on every summary.
2. **"The authorizer is proven, not just written."** The authorizer
   tests run with the SQL-text pre-check disabled, so a pass means
   SQLite itself refused the read. Point to `test_authorizer.py` and
   explain the source-argument rule: a base-table read is allowed
   only when expanded from an allowed view.
3. **"Dedup is a correctness feature, not a convenience."** A second
   cycle produces zero new proposals for the same bands, and the
   summary says so explicitly. Point to
   `test_breach_dedup_no_repeat_alert_same_window` and the
   window-expiry counterpart.
4. **"Consent is parsed, not assumed."** A hedged "maybe" and a
   self-contradicting "yes, wait, no" both fail the gate, and a failed
   gate does not burn the token. Point to `test_gates.py`.
5. **"Security rules came from real bug patterns."** The checklist
   behind this repo — cards and emails on the PII list, negatives
   rejected on cost inputs, non-empty brand blocklist asserted in a
   test, row cap at fetch time — exists because each of those has
   been a real miss in agent codebases before. Say which test proves
   each one.
6. **"Honest scope."** One synthetic portfolio, no live feed, no
   deployment claims. The Built vs Planned table is the honest
   version of a roadmap, and the limitations doc names the restart
   and durability caveats outright.

## Anticipated hard questions

- *"Why not let the agent act on warning breaches?"* Because acting
  and proposing have different blast radii, and the repo's thesis is
  that a monitoring agent earns trust by briefing well before it is
  ever allowed to act. The code enforces that thesis.
- *"What breaks first at scale?"* The in-memory approval store and
  the single-file database: persistence and concurrency are the
  first production investments, and they are listed as Planned.
- *"How do you know the authorizer covers views correctly?"* The
  view-read test passes through a real view, and the direct-read
  tests fail through the same connection — both directions are
  covered, with the text check off.
