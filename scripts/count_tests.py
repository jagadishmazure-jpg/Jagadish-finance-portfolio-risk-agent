"""Print the real test count by collecting (not running) the suite.

Usage: python3 scripts/count_tests.py
"""
import subprocess
import sys

out = subprocess.run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"],
                     capture_output=True, text=True, cwd=".")
lines = [l for l in out.stdout.splitlines() if "::" in l]
print(f"tests collected: {len(lines)}")
