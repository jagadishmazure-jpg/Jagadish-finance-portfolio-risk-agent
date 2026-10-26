# Knowledge notes: portfolio risk monitoring agent (distilled)

Distilled in the author's own words from the pattern of an autonomous
monitoring workflow. No source text is reproduced here; the overlap
check against the source (`scripts/overlap_check.py`) reports 0 hits.

## The pattern, in plain language

A monitoring agent is different from a chatbot and from a fixed
pipeline. A chatbot answers when asked. A pipeline runs the same
steps every time. An agent loops: it forms a small plan, uses tools
to look at the world, reads what came back, and decides what to do
next — then loops again. For portfolio risk, the "world" it looks at
is a set of exposures (how much sits in one sector, one holding, one
asset class, how fast a position could be exited), and the "decide"
step is mostly classification: is anything past a limit, how serious
is it, and has anyone already been told?

## The pieces that matter

- **Tools before cleverness.** The agent needs reliable readers for
  positions and exposures, a place to keep limits, and a ledger it
  writes to as it goes. Without those three, reasoning has nothing to
  stand on and nothing to audit.
- **Memory is the ledger plus the last alert.** Two kinds of memory
  do the work: the run ledger (what the agent did, in order) and the
  alert history (what it already told someone, and when). The second
  one is what stops alert fatigue: the same breach should not page
  the same person every cycle.
- **Limits need tiers, not a single line.** A single threshold gives
  you a cliff: silent, then alarming. Tiers (watch, elevated,
  critical) let the response scale — monitor, acknowledge, escalate —
  instead of treating every crossing as an emergency or none of them
  as one.
- **Summaries are a product, not an afterthought.** A decision-maker
  needs four things: what the exposure is, what crossed a limit, what
  moved since last time, and what is suggested next. If any of the
  four is missing, the briefing creates a follow-up question instead
  of answering one.
- **Oversight is a design input, not a bolt-on.** The place where a
  human must step in has to be decided when the loop is drawn, not
  after it is built. High-severity items wait for a named person;
  everything else is a proposal. The agent's autonomy ends exactly
  where accountability starts, and that boundary should be visible
  in code (a missing execution path, a gate that fails closed), not
  just in a document.

## Failure modes to design against

- **Loops without progress:** the agent re-reading the same state
  and re-alerting forever. Counter: deduplication windows.
- **Alert fatigue:** every cycle producing the same warnings until
  humans stop reading them. Counter: tiers plus suppression, and a
  summary that says plainly when alerts were suppressed and why.
- **Silent drift:** limits that made sense last quarter quietly going
  stale. Counter: limits as explicit, reviewable data (the threshold
  store), not constants buried in code.
- **Authority creep:** a monitoring tool gradually gaining the
  ability to act because "it was convenient". Counter: no execution
  path at all, so convenience cannot quietly become capability.
- **Unauditable reasoning:** an agent that cannot show its steps.
  Counter: the run ledger, appended every phase, readable through a
  view like any other data.

## What this repo takes from the pattern, and what it leaves out

Taken: the loop, the three tools (readers, limit store, ledger), the
tiers, the dedup window, the four-part summary, and the checkpoint
design. Left out on purpose: any language-model call (the loop here
is deterministic, so its behaviour is testable), live data, and any
execution capability. Those are separate decisions with separate
reviews, not defaults.
