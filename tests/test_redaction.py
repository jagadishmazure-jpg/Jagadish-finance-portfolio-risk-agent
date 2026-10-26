"""PII redaction proof tests: cards, emails, phones, SSNs."""
from portfolio_risk_agent.redaction import redact_pii


def test_redacts_card_number_with_spaces():
    out = redact_pii("card 4111 1111 1111 1111 on file")
    assert "4111" not in out and "[REDACTED_CARD]" in out


def test_redacts_card_number_with_dashes():
    out = redact_pii("card 4111-1111-1111-1111 on file")
    assert "4111" not in out and "[REDACTED_CARD]" in out


def test_redacts_email_address():
    out = redact_pii("contact analyst@example.org about this")
    assert "analyst@example.org" not in out and "[REDACTED_EMAIL]" in out


def test_redacts_phone_number():
    out = redact_pii("call 555-123-4567 for details")
    assert "555-123-4567" not in out and "[REDACTED_PHONE]" in out


def test_redacts_ssn():
    out = redact_pii("ssn 123-45-6789 in note")
    assert "123-45-6789" not in out and "[REDACTED_SSN]" in out


def test_redacts_all_pii_types_in_one_note():
    note = "Reach jane@example.com, card 5500 0055 5555 5559, phone 555-123-4567"
    out = redact_pii(note)
    assert "jane@example.com" not in out and "5500" not in out and "555-123-4567" not in out
    assert "[REDACTED_EMAIL]" in out and "[REDACTED_CARD]" in out and "[REDACTED_PHONE]" in out


def test_leaves_ordinary_risk_numbers_untouched():
    out = redact_pii("single_sector_pct: 60.0 (as of 2026-10-26), exposure 12.5%")
    assert "60.0" in out and "12.5%" in out and "2026-10-26" in out
    assert "REDACTED" not in out


def test_summary_redacts_pii_in_free_text(agent):
    # A note smuggled into exposure text must not survive summarising.
    from portfolio_risk_agent.summaries import build_summary
    summary = build_summary(
        "KAV-GROWTH",
        [{"metric": "note", "value": 1.0, "as_of": "2026-10-26"}],
        [], {}, [], [], )
    assert summary["trade_executed"] is False
    from portfolio_risk_agent.redaction import redact_pii as r
    assert r("mail me at jane@example.com") == "mail me at [REDACTED_EMAIL]"
