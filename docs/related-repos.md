# Related repos (cross-links, not duplication)

This repo is one piece of a wider portfolio of agentic-AI reference
implementations. It does not duplicate their material; it links to the
concern each one owns.

- **Fraud detection agents** — anomaly flags and alert triage for
  transaction fraud. Overlap boundary: fraud flags are about
  individual transactions; this repo is about portfolio-level risk
  exposures and limit breaches. Different signal, different loop.
- **Credit memo / underwriting agents** — borrower risk
  classification and explainable credit narratives. Boundary: credit
  decisions are per-borrower; this repo watches aggregate exposures
  and never underwrites anything.
- **Compliance RAG** — grounded answers from regulatory sources with
  citations. Boundary: compliance answers explain rules; this repo
  checks numbers against limits. A future integration could cite the
  rule behind a limit, but the limit-checking logic lives here.
- **KYC/AML pipeline** — staged due-diligence workflows with audit
  trails. Boundary: identity and sanctions screening vs portfolio
  surveillance; the shared pattern is the audit ledger, and the
  ledger design here is deliberately kept independent so each repo
  stays runnable alone.
- **Bank-in-a-box (multi-agent orchestration)** — several agents
  collaborating across analysis, risk, and compliance. Boundary:
  that repo owns multi-agent coordination; this repo owns the
  single-agent monitoring loop that such a system would call as one
  of its workers.
- **Governance proof-of-concept** — evaluating AI initiatives against
  governance, cost, and viability criteria. Boundary: governance
  evaluates the system; this repo is a system to be evaluated.

Repo names above are descriptive; exact repository slugs live on the
owner's profile and are linked from there when this scaffold is
published.
