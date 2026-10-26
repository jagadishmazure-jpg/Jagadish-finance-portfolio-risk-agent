"""Confirmation-gate proof tests: bypass, reject, absent, low, contradicting."""
from datetime import datetime, timedelta, timezone

import pytest

from portfolio_risk_agent.approvals import (
    ApprovalStore, ConfirmationGate, parse_consent,
)

NOW = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


@pytest.fixture()
def gate():
    store = ApprovalStore()
    store.issue("tok-1", "Maya Chen", "review:KAV-GROWTH", ttl_minutes=60, now=NOW)
    return ConfirmationGate(store), store


def test_valid_approval_and_explicit_yes_confirms(gate):
    g, _ = gate
    ok, reason = g.confirm("tok-1", "review:KAV-GROWTH", "yes", now=NOW)
    assert ok is True


def test_gate_bypass_absent_token_rejected(gate):
    g, _ = gate
    ok, reason = g.confirm(None, "review:KAV-GROWTH", "yes", now=NOW)
    assert ok is False and "absent" in reason


def test_gate_bypass_unknown_token_rejected(gate):
    g, _ = gate
    ok, reason = g.confirm("forged-token", "review:KAV-GROWTH", "yes", now=NOW)
    assert ok is False


def test_gate_bypass_wrong_scope_rejected(gate):
    g, _ = gate
    ok, reason = g.confirm("tok-1", "trade:KAV-GROWTH", "yes", now=NOW)
    assert ok is False and "scope" in reason


def test_gate_bypass_expired_token_rejected(gate):
    g, store = gate
    ok, reason = g.confirm("tok-1", "review:KAV-GROWTH", "yes",
                           now=NOW + timedelta(hours=2))
    assert ok is False and "expired" in reason


def test_gate_bypass_reused_token_rejected(gate):
    g, _ = gate
    assert g.confirm("tok-1", "review:KAV-GROWTH", "yes", now=NOW)[0] is True
    ok, reason = g.confirm("tok-1", "review:KAV-GROWTH", "yes", now=NOW)
    assert ok is False and "already used" in reason


def test_gate_reject_explicit_no(gate):
    g, _ = gate
    ok, reason = g.confirm("tok-1", "review:KAV-GROWTH", "no", now=NOW)
    assert ok is False


def test_gate_reject_absent_reply(gate):
    g, _ = gate
    ok, reason = g.confirm("tok-1", "review:KAV-GROWTH", None, now=NOW)
    assert ok is False


def test_gate_reject_low_confidence_reply(gate):
    g, _ = gate
    for reply in ("maybe", "I guess so", "probably yes", "not sure"):
        assert parse_consent(reply) == "low", reply
    ok, _ = g.confirm("tok-1", "review:KAV-GROWTH", "maybe", now=NOW)
    assert ok is False


def test_gate_reject_self_contradicting_consent(gate):
    g, _ = gate
    for reply in ("yes, wait, no", "yes, hold on, no", "yes actually no"):
        assert parse_consent(reply) == "contradicting", reply
    ok, _ = g.confirm("tok-1", "review:KAV-GROWTH", "yes, wait, no", now=NOW)
    assert ok is False


def test_approval_requires_named_person():
    store = ApprovalStore()
    for bad_name in ("admin", "system", "agent", "Al", ""):
        with pytest.raises(ValueError):
            store.issue("t", bad_name, "review:X", now=NOW)


def test_approval_token_not_consumed_on_failed_gate(gate):
    # A rejected gate must not burn the single-use token.
    g, _ = gate
    assert g.confirm("tok-1", "review:KAV-GROWTH", "no", now=NOW)[0] is False
    assert g.confirm("tok-1", "review:KAV-GROWTH", "yes", now=NOW)[0] is True
