# Autonomy trade-offs: what the agent may do alone vs what escalates

## May do alone (no human needed)

- Read exposures and thresholds through the guarded views.
- Compare values with thresholds and classify severity.
- Suppress a repeat alert for a band already alerted in its window.
- Append plan/act/observe/summary rows to the run ledger.
- Build and store a structured summary.
- Produce a proposal for a warning breach.

## Always escalates (never decided alone)

- Anything about a high or critical breach: the proposal stays
  `awaiting_acknowledgement` until a named person acknowledges it.
- Any portfolio change: the agent can only propose; there is no
  execution path, so "escalation" here means a human must take the
  proposal elsewhere and decide.
- Any action whose approval token is missing, expired, reused, or
  scoped to something else: the gate fails closed.
- Any human reply that is hedged, contradictory, unclear, or a "no":
  treated as no consent.

## Why this split

Speed is the agent's job (continuous watching, instant classification,
no repeat noise); judgement under uncertainty is the human's job
(severity interpretation, trade-offs between limits, accountability).
The split is enforced in code, not in prose: the absence of an
execution method and the acknowledgement gate are both tested. The
trade-off this accepts is slower response to high breaches — a
deliberate cost, paid to avoid an autonomous agent moving money or
recommending action on a misread signal.
