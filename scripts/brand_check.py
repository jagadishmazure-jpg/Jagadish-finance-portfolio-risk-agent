"""Brand check: hash every 1-4 word window of repo docs, compare to the
hash-only blocklist in portfolio_risk_agent.brand. No blocked name is
stored in plain text anywhere in this repo or in this script.

Usage: PYTHONPATH=src python3 scripts/brand_check.py [paths ...]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from portfolio_risk_agent.brand import BLOCKED_NAME_HASHES, windows_of, _digest


def main(argv):
    targets = argv[1:] or ["README.md", "docs", "knowledge", "src", "tests"]
    hits = []
    for target in targets:
        paths = []
        if os.path.isfile(target):
            paths = [target]
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                paths += [os.path.join(root, f) for f in files
                          if f.endswith((".md", ".py", ".txt"))]
        for path in paths:
            text = open(path, encoding="utf-8", errors="ignore").read()
            for window in windows_of(text):
                if _digest(window) in BLOCKED_NAME_HASHES:
                    hits.append((path, window))
    for path, window in hits:
        print(f"HIT {path}: {window!r}")
    print(f"brand hits: {len(hits)}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
