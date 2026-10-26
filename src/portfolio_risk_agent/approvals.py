"""Named-person, single-use, scoped, expiring approvals + consent gates.

A confirmation gate passes ONLY when ALL of these hold:
  * an approval token exists (absent -> fail),
  * it names a real person (not "admin", "system", or the agent),
  * it has not been used before (single-use),
  * its scope matches the requested action exactly,
  * it has not expired,
  * AND the human's reply parses as an explicit, confident "yes".

Low-confidence replies ("maybe", "I guess") and self-contradicting
replies ("yes, wait, no") are NOT consent. A "no" is a rejection, and
anything unclear is treated as absent consent.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

_GENERIC_APPROVERS = {"admin", "system", "agent", "user", "approver"}
_AFFIRMATIVE = ("yes", "approved", "approve", "confirm", "confirmed", "go ahead", "acknowledged")
_NEGATIVE = ("no", "reject", "rejected", "decline", "declined", "do not", "stop", "cancel")
_HEDGES = ("maybe", "i guess", "probably", "not sure", "i think so", "unsure", "perhaps")
_CONTRADICTION_MARKERS = ("wait", "hold on", "actually", "on second thought")


def parse_consent(text: str | None) -> str:
    """Return 'yes' | 'no' | 'low' | 'contradicting' | 'unclear'."""
    if text is None:
        return "unclear"
    lowered = " " + re.sub(r"[^a-z ]", " ", text.lower()) + " "
    has_yes = any(f" {word} " in lowered or lowered.strip() == word for word in _AFFIRMATIVE) \
        or any(re.search(rf"\b{re.escape(w)}\b", lowered) for w in _AFFIRMATIVE)
    has_no = any(re.search(rf"\b{re.escape(w)}\b", lowered) for w in _NEGATIVE)
    has_hedge = any(re.search(rf"\b{re.escape(w)}\b", lowered) for w in _HEDGES)
    has_contradiction_marker = any(re.search(rf"\b{re.escape(w)}\b", lowered)
                                   for w in _CONTRADICTION_MARKERS)
    if (has_yes and has_no) or (has_yes and has_contradiction_marker):
        return "contradicting"
    if has_hedge:
        return "low"
    if has_yes and not has_no:
        return "yes"
    if has_no:
        return "no"
    return "unclear"


@dataclass
class Approval:
    token: str
    approver: str  # a named person, e.g. "Maya Chen"
    scope: str
    expires_at: datetime
    used: bool = False

    def __post_init__(self):
        name = (self.approver or "").strip()
        if len(name) < 3 or name.lower() in _GENERIC_APPROVERS or " " not in name:
            raise ValueError("approver must be a named person (first and last name)")
        if not self.scope or not self.token:
            raise ValueError("approval needs a token and a scope")


class ApprovalStore:
    def __init__(self):
        self._approvals: dict[str, Approval] = {}

    def issue(self, token: str, approver: str, scope: str,
              ttl_minutes: int = 60, now: datetime | None = None) -> Approval:
        now = now or datetime.now(timezone.utc)
        approval = Approval(token, approver, scope, now + timedelta(minutes=ttl_minutes))
        self._approvals[token] = approval
        return approval

    def validate(self, token: str | None, scope: str,
                 now: datetime | None = None) -> tuple[bool, str]:
        now = now or datetime.now(timezone.utc)
        if token is None:
            return False, "absent: no approval token supplied"
        approval = self._approvals.get(token)
        if approval is None:
            return False, "absent: unknown approval token"
        if approval.used:
            return False, "rejected: approval already used (single-use)"
        if approval.scope != scope:
            return False, "rejected: approval scope does not match"
        if now >= approval.expires_at:
            return False, "rejected: approval expired"
        return True, "ok"


class ConfirmationGate:
    """Combines token validation with explicit-consent parsing."""

    def __init__(self, store: ApprovalStore):
        self.store = store

    def confirm(self, token: str | None, scope: str, reply: str | None,
                now: datetime | None = None) -> tuple[bool, str]:
        ok, reason = self.store.validate(token, scope, now=now)
        if not ok:
            return False, reason
        consent = parse_consent(reply)
        if consent != "yes":
            return False, f"rejected: consent parsed as {consent!r}, explicit 'yes' required"
        approval = self.store._approvals[token]  # consume exactly once
        approval.used = True
        return True, "confirmed"
