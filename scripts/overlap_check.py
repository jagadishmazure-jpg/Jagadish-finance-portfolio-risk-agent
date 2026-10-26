"""8-word overlap check: repo docs vs an external source text file.

Usage:
    python3 scripts/overlap_check.py <source-text-file> [docs-dir ...]

The source file itself is never committed to the repo. The check slides
an 8-word window over the normalised source text and over every .md
file under the given dirs, and reports any shared window. Target: 0 hits.
"""
import os
import re
import sys


def windows(text, n=8):
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def main(argv):
    if len(argv) < 2:
        print("usage: overlap_check.py <source-text> [docs-dir ...]")
        return 2
    source = open(argv[1], encoding="utf-8", errors="ignore").read()
    source_windows = windows(source)
    dirs = argv[2:] or ["README.md", "docs", "knowledge"]
    hits = []
    for target in dirs:
        paths = []
        if os.path.isfile(target):
            paths = [target]
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                paths += [os.path.join(root, f) for f in files if f.endswith(".md")]
        for path in paths:
            text = open(path, encoding="utf-8", errors="ignore").read()
            for window in sorted(windows(text) & source_windows):
                hits.append((path, window))
    for path, window in hits:
        print(f"HIT {path}: {window!r}")
    print(f"overlap hits: {len(hits)}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
