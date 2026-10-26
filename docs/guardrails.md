# Guardrails and security controls

## 1. View-aware SQLite authorizer (default deny)

The agent's read connection installs a SQLite authorizer. For a column
read, the authorizer allows the read only when the table is an allowed
view or when the read is expanded from an allowed view (the authorizer's
source argument names the view). A direct base-table read has no source
view and is denied. Everything else — writes, PRAGMA, ATTACH, DETACH,
functions including `load_extension`, schema changes — is denied.

A SQL-text pre-check adds defence in depth, but the authorizer tests
run with that pre-check disabled (`enforce_text_check=False`) so they
prove the authorizer alone enforces the policy.

Proof: `tests/test_authorizer.py` — direct base-table read, base-table
read via the query helper, `sqlite_master` read, writes, PRAGMA,
ATTACH, and `load_extension` denial tests.

## 2. Confirmation gates

An approval is valid only when it names a person (first and last name;
"admin"/"system"/"agent" rejected), has not been used, matches the
requested scope exactly, and has not expired. The gate then requires
the human reply to parse as an explicit, confident "yes". Rejected:
unknown/forged tokens (bypass), wrong scope, expired and reused tokens,
explicit "no" (reject), missing token or missing reply (absent),
hedged replies such as "maybe" (low confidence), and self-contradicting
replies such as "yes, wait, no". A failed gate does not consume the
token, so a later clean confirmation can still succeed.

Proof: all `test_gate_*` tests in `tests/test_gates.py`.

## 3. Agent proposes, never executes

There is no trade-execution method anywhere in the package. Proposals
are records with status `proposed` or `awaiting_acknowledgement`, and
every summary carries `trade_executed: false`.

Proof: `tests/test_breach_agent.py::test_agent_never_executes_trades`,
`test_summary_shape_and_no_trade`.

## 4. Human checkpoints for high severity

High and critical breaches stay `awaiting_acknowledgement` until a
named person acknowledges them (`Agent.acknowledge`, which itself
rejects generic names). Warning breaches need no acknowledgement but
still only produce proposals.

Proof: `test_high_breach_awaits_named_acknowledgement`,
`test_named_acknowledgement_clears_checkpoint`,
`test_acknowledgement_requires_named_person`.

## 5. PII redaction

Summaries and outbound messages pass through `redact_pii`, which
masks card numbers, email addresses, phone numbers, and SSNs.

Proof: `tests/test_redaction.py` (all six tests, including the
all-types-in-one-note case and the leave-ordinary-numbers-alone case).

## 6. Row cap at fetch time

`run_view_query` uses `fetchmany(MAX_ROWS + 1)` with `MAX_ROWS = 100`
and returns a truncation flag. No caller query is rewritten to add a
cap, and no full result set is pulled.

Proof: `test_row_cap_returns_max_plus_truncation_flag`,
`test_no_fetchall_and_no_limit_rewriting_in_readers`.

## 7. Cost inputs reject negatives

`validate_cost` rejects negative, NaN, infinite, boolean, and
non-numeric inputs; `RunBudget` additionally refuses overspend.

Proof: `test_negative_cost_rejected`, `test_negative_budget_rejected`,
`test_negative_cost_add_rejected_and_spend_unchanged`,
`test_non_number_and_nan_cost_rejected`.

## 8. Brand guard (hashes only)

Blocked names live in `brand.py` as SHA-256 hashes, never as plain
text. `scripts/brand_check.py` hashes 1–4 word windows of every doc,
code, and test file and reports matches (0 hits at release).

Proof: `test_brand_blocklist_is_non_empty`,
`test_brand_blocklist_contains_no_plain_names`,
`test_brand_check_flags_blocked_and_passes_innocent`.

## 9. Email: dry-run by default, refused in CI, no credentials

`EmailChannel` defaults to `dry_run=True`; queuing needs explicit
`allow_real_send=True`; any send is refused when `CI` is set. The
channel takes no password, token, or secret, and there is no SMTP
transport in this repo — the opt-in path only records to an outbox.

Proof: `test_email_channel_dry_run_by_default`,
`test_email_channel_requires_explicit_opt_in`,
`test_email_channel_refused_in_ci`,
`test_email_channel_takes_no_credentials`,
`test_email_body_is_redacted`.
