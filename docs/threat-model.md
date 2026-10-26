# Threat model

## Assets

- Portfolio exposure and position data (synthetic here; real in any
  adoption).
- The run ledger and alert log (audit trail integrity).
- Approval tokens and acknowledgements (authority to advance a
  proposal).
- Summaries sent to decision-makers (must not leak PII or misstate
  execution).

## STRIDE sketch

| Threat | Mitigation in this repo | Residual risk |
|---|---|---|
| Spoofing (forged approval) | Tokens validated for existence, scope, expiry, single use; approver must be a named person | Token storage is in-memory; theft model for a production store is out of scope |
| Tampering (ledger edits) | Agent writes only via allow-listed, parameterised appends; reads go through views | An operator with the admin connection can edit the file directly — that is an operator-trust boundary, documented, not hidden |
| Repudiation (denied acknowledgement) | Acknowledgements record the named person; ledger records every phase | In-memory acknowledgement store does not survive restart (Planned: persistent audit store) |
| Information disclosure (PII / base tables) | View-aware authorizer; PII redaction on summaries and messages | Brand hash list is exact-match only; redaction patterns cannot catch every PII format |
| Denial of service (unbounded reads) | `fetchmany(MAX_ROWS + 1)` cap with truncation flag | A hostile threshold set could still generate many proposals per cycle; proposal volume caps are Planned |
| Elevation of privilege (agent acts) | No execution method exists; gates fail closed | A future contributor could add an execution path — the `test_agent_never_executes_trades` test exists to catch exactly that |

## Agent-specific risks (OWASP LLM Top 10 flavour)

- **Excessive agency:** addressed by the propose-never-execute rule
  and by the narrow write surface (ledger/alert appends only).
- **Prompt injection via data:** exposure values and notes are data,
  never instructions; summaries redact and never execute embedded
  text. (No LLM is wired in here, so injection surface is limited to
  free-text notes reaching summaries — redaction is the control.)
- **Unbounded consumption:** row cap + budget validation; per-cycle
  cost accounting exists in `costs.py` but is not yet wired into the
  loop (Planned).

## Trust boundaries

1. Operator (owns the database file and admin connection) vs agent
   (guarded read connection + ledger appends only).
2. Agent vs decision-maker (summaries and proposals flow one way;
   authority flows back only through named approvals and
   acknowledgements).
3. Repo vs real world (synthetic data in, no real data or credentials
   anywhere; no outbound transport).
