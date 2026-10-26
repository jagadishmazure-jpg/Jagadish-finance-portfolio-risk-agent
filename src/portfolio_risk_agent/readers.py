"""Position / exposure readers. They only ever query the allowed views.

The caller's query text is never rewritten to cap rows, and the result
set is never pulled in full in this module: the row cap lives in
db.run_view_query (fetchmany).
"""
from __future__ import annotations

from .db import run_view_query


def read_positions(con, portfolio_id):
    rows, truncated = run_view_query(
        con,
        "SELECT portfolio_id, instrument, sector, market_value, weight_pct"
        " FROM v_positions WHERE portfolio_id = ?",
        (portfolio_id,),
    )
    return [
        {"portfolio_id": r[0], "instrument": r[1], "sector": r[2],
         "market_value": r[3], "weight_pct": r[4]}
        for r in rows
    ], truncated


def read_exposures(con, portfolio_id):
    rows, truncated = run_view_query(
        con,
        "SELECT portfolio_id, metric, value, as_of FROM v_exposures WHERE portfolio_id = ?",
        (portfolio_id,),
    )
    return [
        {"portfolio_id": r[0], "metric": r[1], "value": r[2], "as_of": r[3]}
        for r in rows
    ], truncated


def read_thresholds(con, portfolio_id):
    rows, truncated = run_view_query(
        con,
        "SELECT portfolio_id, metric, warn_at, high_at, critical_at, window_hours"
        " FROM v_thresholds WHERE portfolio_id = ?",
        (portfolio_id,),
    )
    return [
        {"portfolio_id": r[0], "metric": r[1], "warn_at": r[2], "high_at": r[3],
         "critical_at": r[4], "window_hours": r[5]}
        for r in rows
    ], truncated


def read_last_alert(con, portfolio_id, metric, band):
    rows, _ = run_view_query(
        con,
        "SELECT alerted_at FROM v_alert_log"
        " WHERE portfolio_id = ? AND metric = ? AND band = ?",
        (portfolio_id, metric, band),
    )
    if not rows:
        return None
    return max(r[0] for r in rows)
