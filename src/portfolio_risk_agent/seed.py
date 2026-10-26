"""Synthetic seed data. Every value here is invented.

Firm: Kavellan Capital (invented for this repo). Instruments use invented
codes, not real tickers. No real portfolio, client, or market data is used.
"""
from __future__ import annotations

SEED_POSITIONS = [
    ("KAV-GROWTH", "KAV-EQ-01", "equity", 420000.0, 42.0),
    ("KAV-GROWTH", "KAV-EQ-02", "equity", 180000.0, 18.0),
    ("KAV-GROWTH", "KAV-FI-01", "fixed_income", 250000.0, 25.0),
    ("KAV-GROWTH", "KAV-FI-02", "fixed_income", 150000.0, 15.0),
]

SEED_EXPOSURES = [
    ("KAV-GROWTH", "single_sector_pct", 60.0, "2026-10-26"),
    ("KAV-GROWTH", "equity_weight_pct", 60.0, "2026-10-26"),
    ("KAV-GROWTH", "top_holding_pct", 42.0, "2026-10-26"),
    ("KAV-GROWTH", "liquidity_days", 4.0, "2026-10-26"),
]

SEED_THRESHOLDS = [
    # portfolio, metric, warn_at, high_at, critical_at, window_hours
    ("KAV-GROWTH", "single_sector_pct", 50.0, 55.0, 65.0, 24.0),
    ("KAV-GROWTH", "equity_weight_pct", 55.0, 65.0, 75.0, 24.0),
    ("KAV-GROWTH", "top_holding_pct", 30.0, 40.0, 50.0, 24.0),
    ("KAV-GROWTH", "liquidity_days", 5.0, 7.0, 10.0, 24.0),
]


def seed(con) -> None:
    con.executemany("INSERT INTO positions VALUES (?, ?, ?, ?, ?)", SEED_POSITIONS)
    con.executemany("INSERT INTO exposures VALUES (?, ?, ?, ?)", SEED_EXPOSURES)
    con.executemany("INSERT INTO thresholds VALUES (?, ?, ?, ?, ?, ?)", SEED_THRESHOLDS)
    con.commit()
