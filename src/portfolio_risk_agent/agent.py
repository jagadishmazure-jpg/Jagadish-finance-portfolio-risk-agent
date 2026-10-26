"""The agent loop: plan -> act -> observe -> repeat.

What the agent does on its own: read exposures and thresholds through
the guarded views, detect breaches, deduplicate alerts inside each
breach window, append ledger rows, and build a structured summary.

What it never does: execute a trade, move money, or change a position.
Proposals are records with status "proposed" (or
"awaiting_acknowledgement" for high/critical breaches). A high or
critical breach needs a named-person acknowledgement before its
proposal may even be shown as ready for a human decision; the agent
still does not act on it. There is intentionally no method on this
class that executes anything against a portfolio.
"""
from __future__ import annotations

from datetime import datetime, timezone

from . import db as dbmod
from .readers import read_exposures, read_thresholds, read_last_alert
from .thresholds import Threshold, detect_breaches, dedup_key, is_duplicate, now_iso
from .summaries import build_summary


class RunLedger:
    """Append-only ledger writer: the agent's only write path."""

    def __init__(self, admin_con):
        self._admin = admin_con

    def append(self, run_id: str, step: str, detail: str) -> None:
        dbmod.append_ledger(self._admin, run_id, step, detail, now_iso())


class Agent:
    def __init__(self, read_con, admin_con, portfolio_id: str = "KAV-GROWTH"):
        self.read_con = read_con
        self.admin_con = admin_con
        self.portfolio_id = portfolio_id
        self.ledger = RunLedger(admin_con)
        self.acknowledgements: dict[str, str] = {}  # breach key -> approver name
        self._previous_values: dict[str, float] = {}

    def acknowledge(self, metric: str, severity: str, approver: str) -> None:
        """Record a named-person acknowledgement of a high/critical breach."""
        name = (approver or "").strip()
        if len(name) < 3 or " " not in name or name.lower() in ("admin", "system", "agent"):
            raise ValueError("acknowledgement requires a named person")
        if severity not in ("high", "critical"):
            raise ValueError("only high/critical breaches need acknowledgement")
        self.acknowledgements[f"{self.portfolio_id}:{metric}:{severity}"] = name

    def run_cycle(self, run_id: str) -> dict:
        # PLAN: read current state through the guarded views.
        self.ledger.append(run_id, "plan", f"read exposures for {self.portfolio_id}")
        exposures, _ = read_exposures(self.read_con, self.portfolio_id)
        threshold_rows, _ = read_thresholds(self.read_con, self.portfolio_id)
        thresholds = [
            Threshold(r["portfolio_id"], r["metric"], r["warn_at"], r["high_at"],
                      r["critical_at"], r["window_hours"])
            for r in threshold_rows
        ]

        # ACT: detect breaches, deduplicate inside each window.
        self.ledger.append(run_id, "act", "detect breaches and deduplicate alerts")
        raw_exposures = [(e["portfolio_id"], e["metric"], e["value"]) for e in exposures]
        breaches = detect_breaches(raw_exposures, thresholds)
        now = datetime.now(timezone.utc)
        new_breaches, proposals = [], []
        deduped_count = 0
        for breach in breaches:
            last = read_last_alert(self.read_con, breach.portfolio_id,
                                   breach.metric, breach.severity)
            if is_duplicate(last, now, breach.threshold.window_hours):
                deduped_count += 1
                continue  # same breach band inside its window: no repeat alert
            new_breaches.append(breach)
            dbmod.append_alert(self.admin_con, breach.portfolio_id, breach.metric,
                               breach.severity, now_iso())
            key = f"{breach.portfolio_id}:{breach.metric}:{breach.severity}"
            acknowledged = key in self.acknowledgements
            status = "proposed" if breach.severity == "warning" or acknowledged \
                else "awaiting_acknowledgement"
            proposals.append({
                "proposal_id": f"{run_id}:{breach.metric}:{breach.severity}",
                "metric": breach.metric,
                "severity": breach.severity,
                "suggested_action": "PROPOSED review of the breaching exposure by the risk owner",
                "status": status,
                "acknowledged_by": self.acknowledgements.get(key),
            })

        # OBSERVE: summarise, and record the observation in the ledger.
        unacknowledged = [
            f"{b.portfolio_id}:{b.metric}:{b.severity}" for b in new_breaches
            if b.severity in ("high", "critical")
            and f"{b.portfolio_id}:{b.metric}:{b.severity}" not in self.acknowledgements
        ]
        summary = build_summary(self.portfolio_id, exposures, new_breaches,
                                self._previous_values, proposals, unacknowledged,
                                deduped_count=deduped_count)
        self.ledger.append(run_id, "observe", f"{len(new_breaches)} new breach alerts")
        self.ledger.append(run_id, "summary", f"{len(proposals)} proposals, none executed")
        for e in exposures:
            self._previous_values[e["metric"]] = e["value"]
        summary["run_id"] = run_id
        return summary
