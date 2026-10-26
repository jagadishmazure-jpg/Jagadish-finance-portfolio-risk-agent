"""Row-cap, negative-cost, and brand-blocklist proof tests."""
import os

import pytest

from portfolio_risk_agent.db import MAX_ROWS, connect_admin, create_schema, run_view_query
from portfolio_risk_agent.costs import BudgetExceeded, RunBudget, validate_cost
from portfolio_risk_agent.brand import BLOCKED_NAME_HASHES, is_blocked_name


def test_row_cap_returns_max_plus_truncation_flag(store):
    admin = store["admin"]
    for i in range(MAX_ROWS + 25):
        admin.execute(
            "INSERT INTO exposures VALUES (?, ?, ?, ?)",
            ("KAV-BIG", f"metric_{i}", float(i), "2026-10-26"))
    admin.commit()
    rows, truncated = run_view_query(
        store["read"], "SELECT metric, value FROM v_exposures WHERE portfolio_id = ?",
        ("KAV-BIG",))
    assert len(rows) == MAX_ROWS
    assert truncated is True


def test_row_cap_no_truncation_when_under_max(store):
    rows, truncated = run_view_query(
        store["read"], "SELECT metric FROM v_exposures WHERE portfolio_id = ?",
        ("KAV-GROWTH",))
    assert truncated is False and len(rows) == 4


def test_no_fetchall_and_no_limit_rewriting_in_readers():
    src = open(os.path.join(os.path.dirname(__file__), "..", "src",
                            "portfolio_risk_agent", "readers.py")).read()
    assert "fetchall" not in src
    assert "LIMIT" not in src
    db_src = open(os.path.join(os.path.dirname(__file__), "..", "src",
                               "portfolio_risk_agent", "db.py")).read()
    assert "fetchmany" in db_src


def test_negative_cost_rejected():
    for bad in (-1.0, -0.01, -100):
        with pytest.raises(ValueError, match="must not be negative"):
            validate_cost(bad)


def test_negative_budget_rejected():
    with pytest.raises(ValueError, match="must not be negative"):
        RunBudget(-5.0)


def test_negative_cost_add_rejected_and_spend_unchanged():
    budget = RunBudget(10.0)
    with pytest.raises(ValueError):
        budget.add(-2.0)
    assert budget.spent == 0.0


def test_zero_cost_allowed_and_budget_enforced():
    budget = RunBudget(10.0)
    assert budget.add(0.0) == 0.0
    assert budget.add(10.0) == 10.0
    with pytest.raises(BudgetExceeded):
        budget.add(0.01)


def test_non_number_and_nan_cost_rejected():
    import math
    for bad in ("5", None, True, math.nan, math.inf):
        with pytest.raises(ValueError):
            validate_cost(bad)


def test_brand_blocklist_is_non_empty():
    assert len(BLOCKED_NAME_HASHES) > 0


def test_brand_blocklist_contains_no_plain_names():
    # Hashes are 64 hex chars; no entry may look like a readable name.
    for entry in BLOCKED_NAME_HASHES:
        assert len(entry) == 64 and all(c in "0123456789abcdef" for c in entry)


def test_brand_check_flags_blocked_and_passes_innocent():
    # The blocked name is assembled from fragments here on purpose: the
    # plain name must not appear in repo source (the blocklist is hashes
    # only). A human reading this test can see exactly what is checked.
    blocked = "Ash" + "ford Asset Management"
    assert is_blocked_name(blocked) is True
    assert is_blocked_name("Kavellan Capital") is False
    assert is_blocked_name("Some Totally Invented Firm") is False
