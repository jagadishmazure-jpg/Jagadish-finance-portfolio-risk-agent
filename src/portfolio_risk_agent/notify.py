"""Email channel: dry-run by default, explicit opt-in to queue, refused in CI.

There is deliberately NO SMTP transport and NO credential handling in
this module: the constructor takes no password, token, or secret of any
kind. With ``dry_run=True`` (the default) a message is recorded as a
dry-run record and nothing is sent. With ``dry_run=False`` the caller
must also pass ``allow_real_send=True``; even then the message is only
recorded in an outbox list for a future transport to pick up, and the
call is refused outright when the CI environment variable is set.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from .redaction import redact_pii


@dataclass
class SentRecord:
    recipient: str
    subject: str
    body: str
    mode: str  # "dry_run" | "queued"


class EmailChannel:
    def __init__(self, dry_run: bool = True, allow_real_send: bool = False):
        self.dry_run = dry_run
        self.allow_real_send = allow_real_send
        self.outbox: list[SentRecord] = []

    def send(self, recipient: str, subject: str, body: str) -> SentRecord:
        if os.environ.get("CI", "").lower() in ("true", "1", "yes"):
            raise RuntimeError("email sending is refused in CI")
        record = SentRecord(recipient, subject, redact_pii(body), "dry_run")
        if self.dry_run:
            self.outbox.append(record)
            return record
        if not self.allow_real_send:
            raise RuntimeError(
                "refusing to queue email: pass allow_real_send=True explicitly to opt in")
        record = SentRecord(recipient, subject, redact_pii(body), "queued")
        self.outbox.append(record)
        return record
