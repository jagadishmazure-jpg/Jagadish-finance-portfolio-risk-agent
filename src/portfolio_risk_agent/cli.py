"""Demo entry point: runs the agent on synthetic data and prints summaries.

Usage (from the repo root):
    PYTHONPATH=src python3 -m portfolio_risk_agent.cli --cycles 2
"""
from __future__ import annotations

import argparse
import json
import sys

from .db import connect_admin, connect_read, create_schema
from .seed import seed
from .agent import Agent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Portfolio risk monitoring agent (synthetic demo)")
    parser.add_argument("--cycles", type=int, default=2)
    parser.add_argument("--portfolio", default="KAV-GROWTH")
    args = parser.parse_args(argv)
    # Demo state lives in a temp file so the guarded read connection and
    # the admin connection see the same database.
    return run_demo(args.cycles, args.portfolio)


def run_demo(cycles: int = 2, portfolio: str = "KAV-GROWTH") -> int:
    import os
    import tempfile
    path = os.path.join(tempfile.gettempdir(), "kavellan_risk_demo.db")
    if os.path.exists(path):
        os.remove(path)
    admin = connect_admin(path)
    create_schema(admin)
    seed(admin)
    read_con = connect_read(path)
    agent = Agent(read_con, admin, portfolio)
    for i in range(1, cycles + 1):
        summary = agent.run_cycle(f"demo-run-{i}")
        print(f"--- cycle {i} ---")
        print(json.dumps(summary, indent=2, sort_keys=True))
    admin.close()
    read_con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
