# Architecture Decision Records

## ADR-1: SQLite + views as the data layer

**Decision:** store state in SQLite and expose it to the agent only
through views, guarded by a SQLite authorizer.
**Why:** the smallest possible dependency (stdlib), and the
authorizer gives a real enforcement point rather than a convention.
**Consequence:** single-file durability caveats (see limitations);
a production adoption would keep the view/authorizer pattern and
swap the store, not drop the guard.

## ADR-2: Authorizer over text scanning

**Decision:** the SQLite authorizer is the enforcement mechanism;
the SQL-text pre-check is defence in depth only.
**Why:** text scans are bypassable by construction (comments,
casing, encoding); the authorizer sees the parsed operation.
**Consequence:** tests must run with the text check disabled to
prove the authorizer alone holds — and they do.

## ADR-3: Propose, never execute

**Decision:** no trade-execution function exists in the package.
**Why:** a monitoring agent's trust comes from briefing quality; an
execution path would change the threat model, the approval model,
and the audit requirements all at once.
**Consequence:** adopters who want execution must add it as a
separate, separately approved component — they cannot "enable" it
here by flipping a flag, because there is no flag.

## ADR-4: Deduplication by (portfolio, metric, severity band) window

**Decision:** one alert per band per window, keyed on the alert log.
**Why:** risk teams drown in repeat alerts; a repeated identical
alert carries no new information and trains people to ignore the
channel.
**Consequence:** a worsening value inside the same band does not
re-alert until the window expires or the band changes. The summary
says this explicitly so nobody mistakes suppression for safety.

## ADR-5: Fail-closed consent parsing

**Decision:** only an explicit, confident "yes" counts; hedged,
contradictory, unclear, and negative replies all fail the gate, and
a failed gate does not consume the token.
**Why:** in a financial workflow, ambiguous consent must not be
rounded up to consent.
**Consequence:** slightly more friction for humans (a "maybe" needs
a clean re-confirmation), accepted deliberately.

## ADR-6: Hash-only brand blocklist

**Decision:** blocked names are stored as SHA-256 hashes; checks
hash candidate windows and compare.
**Why:** the repo must not itself publish the list of names it
refuses to use.
**Consequence:** exact-match only; paraphrases slip through, and
that limitation is documented rather than papered over.

## ADR-7: Dry-run email with no transport

**Decision:** the notification channel defaults to dry-run, refuses
in CI, takes no credentials, and ships no SMTP code.
**Why:** a scaffold must not be able to leak data or credentials by
accident; adding a transport is an adopter decision with its own
review.
**Consequence:** "notifications sent" can never be claimed from this
repo — only "notifications recorded".
