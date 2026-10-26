"""Autonomous portfolio risk monitoring agent (synthetic data only).

The agent watches risk exposures, flags threshold breaches, and writes
structured summaries for human decision-makers. It proposes portfolio
changes; it never executes a trade. There is no trade-execution function
anywhere in this package, by design.
"""

from .db import MAX_ROWS, connect_read, connect_admin, create_schema
from .thresholds import Threshold, ThresholdStore, detect_breaches, Breach
from .approvals import Approval, ApprovalStore, ConfirmationGate, parse_consent
from .redaction import redact_pii
from .summaries import build_summary
from .costs import validate_cost, RunBudget
from .notify import EmailChannel
from .agent import Agent, RunLedger

__version__ = "0.1.0"

__all__ = [
    "MAX_ROWS", "connect_read", "connect_admin", "create_schema",
    "Threshold", "ThresholdStore", "detect_breaches", "Breach",
    "Approval", "ApprovalStore", "ConfirmationGate", "parse_consent",
    "redact_pii", "build_summary", "validate_cost", "RunBudget",
    "EmailChannel", "Agent", "RunLedger",
]
