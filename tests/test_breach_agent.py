"""Breach detection, deduplication, agent loop, and never-executes proof."""
import inspect

from portfolio_risk_agent.agent import Agent
from portfolio_risk_agent.approvals import ApprovalStore, ConfirmationGate
from portfolio_risk_agent.db import append_ledger
from portfolio_risk_agent.notify import EmailChannel
from portfolio_risk_agent.thresholds import Threshold, detect_breaches, severity_for
import portfolio_risk_agent.agent as agent_mod
import pytest


def _threshold(metric="single_sector_pct"):
    return Threshold("KAV-GROWTH", metric, 50.0, 55.0, 65.0, 24.0)


def test_severity_tiers():
    t = _threshold()
    assert severity_for(49.9, t) is None
    assert severity_for(50.0, t) == "warning"
    assert severity_for(55.0, t) == "high"
    assert severity_for(65.0, t) == "critical"


def test_threshold_ordering_and_negative_rejected():
    with pytest.raises(ValueError):
        Threshold("P", "m", 60.0, 50.0, 70.0)
    with pytest.raises(ValueError):
        Threshold("P", "m", -1.0, 50.0, 70.0)


def test_detect_breaches_skips_unknown_metrics():
    breaches = detect_breaches([("KAV-GROWTH", "unknown_metric", 99.0)], [_threshold()])
    assert breaches == []


def test_agent_cycle_finds_seeded_breaches(agent):
    summary = agent.run_cycle("run-1")
    severities = {p["severity"] for p in summary["proposals"]}
    assert severities == {"high", "warning"}
    assert summary["requires_acknowledgement"] is True
    assert summary["trade_executed"] is False


def test_breach_dedup_no_repeat_alert_same_window(agent):
    first = agent.run_cycle("run-1")
    assert len(first["proposals"]) == 3
    second = agent.run_cycle("run-2")
    assert second["proposals"] == []
    assert second["suppressed_repeat_alerts"] == 3
    assert "already alerted" in second["suggested_next_step"]


def test_breach_repeats_after_window_expires(agent, store):
    agent.run_cycle("run-1")
    # Backdate the alert log beyond the 24h window, then re-run.
    store["admin"].execute("UPDATE alert_log SET alerted_at = '2020-01-01T00:00:00+00:00'")
    store["admin"].commit()
    summary = agent.run_cycle("run-2")
    assert len(summary["proposals"]) == 3


def test_high_breach_awaits_named_acknowledgement(agent):
    summary = agent.run_cycle("run-1")
    high = [p for p in summary["proposals"] if p["severity"] == "high"]
    assert high and all(p["status"] == "awaiting_acknowledgement" for p in high)
    assert summary["unacknowledged_high_breaches"]


def test_named_acknowledgement_clears_checkpoint(agent, store):
    agent.acknowledge("single_sector_pct", "high", "Maya Chen")
    agent.acknowledge("top_holding_pct", "high", "Maya Chen")
    summary = agent.run_cycle("run-1")
    assert summary["requires_acknowledgement"] is False
    high = [p for p in summary["proposals"] if p["severity"] == "high"]
    assert all(p["status"] == "proposed" and p["acknowledged_by"] == "Maya Chen" for p in high)


def test_acknowledgement_requires_named_person(agent):
    for bad in ("admin", "system", "Al", ""):
        with pytest.raises(ValueError):
            agent.acknowledge("single_sector_pct", "high", bad)


def test_agent_never_executes_trades():
    # No execution method exists on the agent, and no proposal is executed.
    assert not hasattr(Agent, "execute_trade")
    assert not hasattr(Agent, "place_order")
    assert "execute_trade" not in open(agent_mod.__file__).read()


def test_summary_shape_and_no_trade(agent):
    summary = agent.run_cycle("run-1")
    for key in ("exposure", "breach", "what_changed", "suggested_next_step"):
        assert key in summary
    assert summary["trade_executed"] is False
    assert all(p["status"] in ("proposed", "awaiting_acknowledgement")
               for p in summary["proposals"])


def test_what_changed_tracks_previous_cycle(agent, store):
    agent.run_cycle("run-1")
    store["admin"].execute(
        "UPDATE exposures SET value = 62.0 WHERE metric = 'single_sector_pct'")
    store["admin"].commit()
    # Backdate alerts so the breach is reported again, with a new value.
    store["admin"].execute("UPDATE alert_log SET alerted_at = '2020-01-01T00:00:00+00:00'")
    store["admin"].commit()
    summary = agent.run_cycle("run-2")
    changed = [line for line in summary["what_changed"]
               if line.startswith("single_sector_pct")]
    assert changed and "60.0 -> 62.0" in changed[0]


def test_ledger_appends_only_allow_listed_steps(store):
    with pytest.raises(ValueError):
        append_ledger(store["admin"], "r", "drop_table", "x", "2026-10-26T00:00:00+00:00")
    append_ledger(store["admin"], "r", "plan", "ok", "2026-10-26T00:00:00+00:00")
    rows, _ = __import__("portfolio_risk_agent.db", fromlist=["run_view_query"]).run_view_query(
        store["read"], "SELECT step FROM v_run_ledger WHERE run_id = ?", ("r",))
    assert rows == [("plan",)]


def test_ledger_records_each_loop_phase(agent, store):
    agent.run_cycle("run-1")
    rows, _ = __import__("portfolio_risk_agent.db", fromlist=["run_view_query"]).run_view_query(
        store["read"], "SELECT step FROM v_run_ledger WHERE run_id = ?", ("run-1",))
    steps = [r[0] for r in rows]
    assert {"plan", "act", "observe", "summary"} <= set(steps)


def test_email_channel_dry_run_by_default():
    channel = EmailChannel()
    assert channel.dry_run is True
    record = channel.send("risk@example.org", "Risk summary", "body")
    assert record.mode == "dry_run" and len(channel.outbox) == 1


def test_email_channel_requires_explicit_opt_in():
    channel = EmailChannel(dry_run=False)
    with pytest.raises(RuntimeError, match="allow_real_send"):
        channel.send("risk@example.org", "Risk summary", "body")


def test_email_channel_refused_in_ci(monkeypatch):
    # The meaningful CI case is an opted-in real send, not a dry run:
    # a dry run transmits nothing, so it must not raise (see the
    # dry-run-in-CI test below). CI must still refuse the real send.
    monkeypatch.setenv("CI", "true")
    channel = EmailChannel(dry_run=False, allow_real_send=True)
    with pytest.raises(RuntimeError, match="refused in CI"):
        channel.send("risk@example.org", "Risk summary", "body")


def test_email_dry_run_records_even_in_ci(monkeypatch):
    # Regression: the runner sets CI, and a dry run must still return
    # its record instead of raising, because it transmits nothing.
    monkeypatch.setenv("CI", "true")
    channel = EmailChannel()
    record = channel.send("risk@example.org", "Risk summary", "body")
    assert record.mode == "dry_run" and len(channel.outbox) == 1


def test_email_channel_takes_no_credentials():
    params = inspect.signature(EmailChannel.__init__).parameters
    assert not any("password" in p or "secret" in p or "token" in p or "api_key" in p
                   for p in params)


def test_email_body_is_redacted():
    channel = EmailChannel()
    record = channel.send("risk@example.org", "Note", "contact jane@example.com")
    assert "jane@example.com" not in record.body and "[REDACTED_EMAIL]" in record.body
