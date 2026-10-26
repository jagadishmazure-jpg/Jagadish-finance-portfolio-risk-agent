# Patterns reused from the wider portfolio (distilled, not copied)

- **Ledger-first agents.** Every agent loop in this portfolio family
  appends a phase-stamped ledger row before it claims to have done
  anything. The portfolio risk agent follows the same rule: plan,
  act, observe, summary — in that order, every cycle.
- **Fail-closed gates.** Confirmation gates across these repos share
  one rule: ambiguous input is not consent. The risk agent's gate
  adds the financial variant — hedged and self-contradicting replies
  fail, and a failed gate never consumes a single-use token.
- **View-only reads.** The pattern of exposing data to an agent
  through views, with the database itself refusing anything else,
  is reused here in its strictest form (authorizer-tested with the
  text check off).
- **Synthetic-first demos.** Every repo in the family runs offline on
  invented data with no credentials. The risk agent's demo database
  is a temp file, created and seeded at run time, and deleted on the
  next run.
