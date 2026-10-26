"""Structured risk summaries for decision-makers.

Every summary carries the same four sections: exposure, breach,
what changed, and a suggested next step. The next step is always a
suggestion for a human to decide on. ``trade_executed`` is always
False: this agent does not place trades, and no summary may claim
otherwise. All free text is PII-redacted before it is returned.
"""
from __future__ import annotations

from .redaction import redact_pii

NEXT_STEP_BY_SEVERITY = {
    "critical": "Escalate to the named risk owner immediately; do not wait for the next cycle.",
    "high": "Seek named-person acknowledgement, then review the position with the risk owner.",
    "warning": "Monitor on the next cycle and review at the next scheduled risk review.",
}


def build_summary(portfolio_id, exposures, breaches, previous_values, proposals,
                  unacknowledged_high, deduped_count=0):
    """breaches: Breach objects. previous_values: {metric: value} from last cycle."""
    exposure_lines = [
        f"{e['metric']}: {e['value']} (as of {e['as_of']})" for e in exposures
    ]
    breach_lines = []
    changed_lines = []
    for breach in breaches:
        breach_lines.append(
            f"{breach.severity.upper()} breach: {breach.metric} = {breach.value}"
            f" (warn {breach.threshold.warn_at}, high {breach.threshold.high_at},"
            f" critical {breach.threshold.critical_at})"
        )
        previous = previous_values.get(breach.metric)
        if previous is None:
            changed_lines.append(f"{breach.metric}: first observation in this ledger")
        elif previous != breach.value:
            changed_lines.append(
                f"{breach.metric}: {previous} -> {breach.value} (change {breach.value - previous:+})"
            )
        else:
            changed_lines.append(f"{breach.metric}: unchanged at {breach.value}")
    top_severity = "critical" if any(b.severity == "critical" for b in breaches) \
        else "high" if any(b.severity == "high" for b in breaches) \
        else "warning" if breaches else None
    summary = {
        "portfolio_id": portfolio_id,
        "exposure": [redact_pii(line) for line in exposure_lines],
        "breach": [redact_pii(line) for line in breach_lines],
        "what_changed": [redact_pii(line) for line in changed_lines],
        "suggested_next_step": NEXT_STEP_BY_SEVERITY.get(top_severity) or (
            "Breaches persist but were already alerted inside their window;"
            " no repeat alert sent this cycle." if deduped_count
            else "No breach: continue routine monitoring."),
        "suppressed_repeat_alerts": deduped_count,
        "proposals": proposals,  # proposals only; nothing here is executed
        "requires_acknowledgement": bool(unacknowledged_high),
        "unacknowledged_high_breaches": unacknowledged_high,
        "trade_executed": False,
    }
    return summary
