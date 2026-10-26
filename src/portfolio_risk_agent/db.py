"""SQLite access with a strict view-aware authorizer.

Read path (the agent's path):
  * Only SELECT statements through the authorizer connection.
  * A base-table column read is allowed ONLY when the authorizer's
    source argument (the view the read is expanded from) names an
    allowed view. A direct read of a base table has no source view and
    is denied by the authorizer itself, not by a text scan.
  * sqlite_master, writes, PRAGMA, ATTACH, DETACH, functions such as
    load_extension, and every other action are denied by default.

An optional SQL-text pre-check sits in front of the authorizer as
defence in depth. It can be switched off (``enforce_text_check=False``)
so tests can prove the authorizer alone enforces the policy; the
authorizer tests in this repo run exactly that way.

Writes exist in exactly one place: ``append_ledger`` / ``append_alert``,
which run on a separate admin connection, take no SQL text from the
caller, and only insert into the run-ledger / alert-log tables with
parameterised queries and an allow-listed step name.
"""
from __future__ import annotations

import re
import sqlite3

MAX_ROWS = 100

ALLOWED_VIEWS = frozenset({
    "v_positions",
    "v_exposures",
    "v_thresholds",
    "v_run_ledger",
    "v_alert_log",
})

ALLOWED_ACTIONS = frozenset({
    sqlite3.SQLITE_SELECT,      # 21
    sqlite3.SQLITE_TRANSACTION,  # 22
})

LEDGER_STEPS = frozenset({"plan", "act", "observe", "summary", "checkpoint", "alert"})

_TEXT_DENIED = (
    "sqlite_master", "pragma", "attach", "detach", "insert", "update",
    "delete", "drop", "alter", "create", "replace", "vacuum", "reindex",
    "load_extension", "writefile", "readfile",
)


def _authorizer(action, table, column, db_name, source):
    """View-aware authorizer: default deny, narrow allow-list."""
    if action == sqlite3.SQLITE_READ:
        # A read of a view itself, or a base-table read expanded from an
        # allowed view (source names the view), is permitted. A direct
        # base-table read has source None and is denied.
        if table in ALLOWED_VIEWS or source in ALLOWED_VIEWS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    if action in ALLOWED_ACTIONS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def _check_text(sql: str) -> None:
    lowered = sql.lower()
    for token in _TEXT_DENIED:
        if re.search(r"\b" + re.escape(token) + r"\b", lowered):
            raise ValueError(f"refused SQL text containing forbidden token: {token}")
    if ";" in sql.strip().rstrip(";"):
        # Only a single trailing semicolon is tolerated; multi-statement
        # text is refused.
        body = sql.strip()
        if body.count(";") > 1 or not body.endswith(";"):
            raise ValueError("refused multi-statement SQL text")


_TEXT_CHECK: dict[int, bool] = {}


def connect_read(path: str = ":memory:", enforce_text_check: bool = True) -> sqlite3.Connection:
    """Return the agent's read-only, authorizer-guarded connection.

    (sqlite3.Connection objects do not accept arbitrary attributes, so
    the text-check flag is kept in a small id-keyed registry.)
    """
    con = sqlite3.connect(path)
    con.set_authorizer(_authorizer)
    _TEXT_CHECK[id(con)] = enforce_text_check
    return con


def run_view_query(con: sqlite3.Connection, sql: str, params=()):
    """Run one SELECT through the guarded connection with a row cap.

    Uses fetchmany(MAX_ROWS + 1) and never pulls the whole result set,
    and never rewrites the caller's SQL to cap rows. Returns (rows, truncated).
    """
    if _TEXT_CHECK.get(id(con), True):
        _check_text(sql)
    if not sql.strip().lower().startswith("select"):
        raise ValueError("only SELECT statements are permitted on the read connection")
    cur = con.execute(sql, params)
    batch = cur.fetchmany(MAX_ROWS + 1)
    truncated = len(batch) > MAX_ROWS
    return batch[:MAX_ROWS], truncated


def connect_admin(path: str = ":memory:") -> sqlite3.Connection:
    """Admin connection used only by schema setup and ledger appends."""
    return sqlite3.connect(path)


def create_schema(con: sqlite3.Connection) -> None:
    con.executescript("""
        CREATE TABLE IF NOT EXISTS positions (
            portfolio_id TEXT, instrument TEXT, sector TEXT,
            market_value REAL, weight_pct REAL
        );
        CREATE TABLE IF NOT EXISTS exposures (
            portfolio_id TEXT, metric TEXT, value REAL, as_of TEXT
        );
        CREATE TABLE IF NOT EXISTS thresholds (
            portfolio_id TEXT, metric TEXT,
            warn_at REAL, high_at REAL, critical_at REAL, window_hours REAL
        );
        CREATE TABLE IF NOT EXISTS run_ledger (
            run_id TEXT, step TEXT, detail TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS alert_log (
            portfolio_id TEXT, metric TEXT, band TEXT, alerted_at TEXT
        );
        CREATE VIEW IF NOT EXISTS v_positions AS
            SELECT portfolio_id, instrument, sector, market_value, weight_pct FROM positions;
        CREATE VIEW IF NOT EXISTS v_exposures AS
            SELECT portfolio_id, metric, value, as_of FROM exposures;
        CREATE VIEW IF NOT EXISTS v_thresholds AS
            SELECT portfolio_id, metric, warn_at, high_at, critical_at, window_hours FROM thresholds;
        CREATE VIEW IF NOT EXISTS v_run_ledger AS
            SELECT run_id, step, detail, created_at FROM run_ledger;
        CREATE VIEW IF NOT EXISTS v_alert_log AS
            SELECT portfolio_id, metric, band, alerted_at FROM alert_log;
    """)
    con.commit()


def append_ledger(con: sqlite3.Connection, run_id: str, step: str, detail: str, created_at: str) -> None:
    """The ONLY write the agent performs: one ledger row, allow-listed step."""
    if step not in LEDGER_STEPS:
        raise ValueError(f"ledger step not allow-listed: {step!r}")
    con.execute(
        "INSERT INTO run_ledger (run_id, step, detail, created_at) VALUES (?, ?, ?, ?)",
        (run_id, step, detail, created_at),
    )
    con.commit()


def append_alert(con: sqlite3.Connection, portfolio_id: str, metric: str, band: str, alerted_at: str) -> None:
    con.execute(
        "INSERT INTO alert_log (portfolio_id, metric, band, alerted_at) VALUES (?, ?, ?, ?)",
        (portfolio_id, metric, band, alerted_at),
    )
    con.commit()
