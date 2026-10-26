# How to run

Offline first. Everything below needs only the standard library and
the system Python; there is no install step and no network call.

```bash
# Full suite (59 tests)
python3 -m pytest tests -q

# Demo: two agent cycles on synthetic data
PYTHONPATH=src python3 -m portfolio_risk_agent.cli --cycles 2

# Checks (source text file is supplied by the operator, never committed)
python3 scripts/overlap_check.py <path-to-source-text>
PYTHONPATH=src python3 scripts/brand_check.py
python3 scripts/count_tests.py
```

## Optional cloud use

None. There is no cloud path in this repo: no provider SDK, no
deployment manifest, no hosted demo. Adding one would be a separate,
explicitly approved change, and would not change the agent's
propose-never-execute rule.
