"""Threshold-breach detection with severity tiers and deduplication."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Threshold:
    portfolio_id: str
    metric: str
    warn_at: float
    high_at: float
    critical_at: float
    window_hours: float = 24.0

    def __post_init__(self):
        for name, value in (("warn_at", self.warn_at), ("high_at", self.high_at),
                            ("critical_at", self.critical_at)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"{name} must be a number")
            if value < 0:
                raise ValueError(f"{name} must not be negative")
        if not (self.warn_at <= self.high_at <= self.critical_at):
            raise ValueError("thresholds must be ordered: warn_at <= high_at <= critical_at")
        if self.window_hours <= 0:
            raise ValueError("window_hours must be positive")


@dataclass(frozen=True)
class Breach:
    portfolio_id: str
    metric: str
    value: float
    severity: str  # "warning" | "high" | "critical"
    threshold: Threshold


def severity_for(value: float, threshold: Threshold) -> str | None:
    if value >= threshold.critical_at:
        return "critical"
    if value >= threshold.high_at:
        return "high"
    if value >= threshold.warn_at:
        return "warning"
    return None


def detect_breaches(exposures, thresholds):
    """exposures: iterable of (portfolio_id, metric, value). Returns Breach list."""
    by_key = {(t.portfolio_id, t.metric): t for t in thresholds}
    breaches = []
    for portfolio_id, metric, value in exposures:
        threshold = by_key.get((portfolio_id, metric))
        if threshold is None:
            continue
        severity = severity_for(value, threshold)
        if severity is not None:
            breaches.append(Breach(portfolio_id, metric, value, severity, threshold))
    return breaches


class ThresholdStore:
    """In-memory threshold registry with validation on every write."""

    def __init__(self):
        self._store: dict[tuple[str, str], Threshold] = {}

    def set(self, threshold: Threshold) -> None:
        self._store[(threshold.portfolio_id, threshold.metric)] = threshold

    def get(self, portfolio_id: str, metric: str) -> Threshold | None:
        return self._store.get((portfolio_id, metric))

    def all(self) -> list[Threshold]:
        return list(self._store.values())


def dedup_key(breach: Breach) -> tuple[str, str, str]:
    """One alert per (portfolio, metric, severity band) per window."""
    return (breach.portfolio_id, breach.metric, breach.severity)


def is_duplicate(last_alerted_at: str | None, now: datetime, window_hours: float) -> bool:
    """True when the same breach band was already alerted inside its window."""
    if last_alerted_at is None:
        return False
    previous = datetime.fromisoformat(last_alerted_at)
    if previous.tzinfo is None:
        previous = previous.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now - previous < timedelta(hours=window_hours)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
