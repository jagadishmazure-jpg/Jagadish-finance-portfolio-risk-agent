"""PII redaction for agent output. Checklist covers, at minimum:

card numbers, email addresses, phone numbers, and SSNs. Anything the
patterns match is replaced before a summary is built or a message is
sent; raw values never reach decision-maker output.
"""
from __future__ import annotations

import re

_PATTERNS = [
    # Card numbers: 13-19 digits, optionally grouped with spaces/dashes.
    (re.compile(r"\b(?:\d[ -]?){12,18}\d\b"), "[REDACTED_CARD]"),
    # Email addresses.
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    # SSN.
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    # Phone numbers: optional country code, area code, 7-digit local part.
    (re.compile(r"(?<!\d)(?:\+?1[-. ]?)?(?:\(?\d{3}\)?[-. ])\d{3}[-. ]\d{4}(?!\d)"),
     "[REDACTED_PHONE]"),
]


def redact_pii(text: str) -> str:
    if text is None:
        return ""
    out = str(text)
    for pattern, replacement in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out
