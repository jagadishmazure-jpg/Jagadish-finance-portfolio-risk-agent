"""Authorizer proof tests.

These tests run with the SQL-text pre-check DISABLED
(enforce_text_check=False), so a pass proves the SQLite authorizer
itself enforces the policy -- not a string scan in front of it.
"""
import sqlite3

import pytest

from portfolio_risk_agent.db import connect_read, run_view_query


@pytest.fixture()
def raw(store):
    # Re-open the read connection with the text check disabled.
    store["read"].close()
    con = connect_read(store["path"], enforce_text_check=False)
    yield con
    con.close()


def test_view_read_allowed_with_text_check_disabled(raw):
    rows, truncated = run_view_query(
        raw, "SELECT portfolio_id, metric, value FROM v_exposures")
    assert rows and truncated is False


def test_direct_base_table_read_denied_by_authorizer(raw):
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("SELECT * FROM positions").fetchall()


def test_direct_base_table_read_denied_via_view_query(raw):
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        run_view_query(raw, "SELECT * FROM positions")


def test_sqlite_master_read_denied_by_authorizer(raw):
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("SELECT name FROM sqlite_master").fetchall()


def test_write_denied_by_authorizer(raw):
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("INSERT INTO positions VALUES ('x','y','z',1.0,1.0)")
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("UPDATE positions SET weight_pct = 99 WHERE portfolio_id = 'KAV-GROWTH'")
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("DELETE FROM positions")


def test_pragma_denied_by_authorizer(raw):
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("PRAGMA table_info(positions)").fetchall()


def test_attach_denied_by_authorizer(raw):
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("ATTACH DATABASE ':memory:' AS other")


def test_load_extension_function_denied_by_authorizer(raw):
    with pytest.raises(sqlite3.DatabaseError, match="prohibited|not authorized"):
        raw.execute("SELECT load_extension('x')").fetchall()


def test_text_check_also_refuses_forbidden_tokens(store):
    # Defence in depth: with the default (enabled) connection, the text
    # check refuses before the authorizer is even consulted.
    with pytest.raises(ValueError, match="forbidden token"):
        run_view_query(store["read"], "SELECT * FROM sqlite_master")
    with pytest.raises(ValueError, match="forbidden token"):
        run_view_query(store["read"], "PRAGMA table_info(positions)")
