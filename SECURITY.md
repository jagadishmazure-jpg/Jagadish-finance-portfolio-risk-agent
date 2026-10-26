# Security policy

## Scope

This is a synthetic-data demo with no live services, no credentials,
and no network access. It is not financial advice and must not be
connected to real portfolios, real accounts, or real trading systems
without a separate security review.

## Reporting a vulnerability

Open an issue describing the concern without including any real
personal, account, or credential data. If the issue involves a
guardrail bypass (authorizer, confirmation gate, redaction, row cap),
a failing-test reproduction is the most useful report you can file.

## What is enforced, and where it is proven

See `docs/guardrails.md` for the control list and the named proof
test for each control. If a README claim ever lacks a named test,
treat the claim as unproven and file an issue saying so.
