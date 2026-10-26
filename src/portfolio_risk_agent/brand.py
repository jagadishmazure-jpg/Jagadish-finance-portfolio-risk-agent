"""Brand-name guard: the blocklist is stored as SHA-256 hashes only.

Plain blocked names never appear in this repo. ``is_blocked_name`` hashes
a candidate name (normalised: lower-cased, non-alphanumerics collapsed)
and compares hashes. ``scripts/brand_check.py`` extends the same idea to
whole documents by hashing every 1-4 word window of each doc file and
reporting any window whose hash is in this set. Limitation, stated
plainly: a hash list cannot catch paraphrases or names absent from the
list; it catches exact blocked names, which is what it is for.
"""
from __future__ import annotations

import hashlib
import re

BLOCKED_NAME_HASHES = frozenset({
    # Hashes of real firm / programme names that must not appear in this
    # repo. The names themselves are intentionally not stored here.
    "c952a08fdb0ff916b78a489ff321a4eb73d258612ededdd834c5a7c55fbc6c70",
    "17e9b17189f2f67e00b4c8dce8a6bedb38051ee221602fd52c88650ef9f68687",
    "b284e172a36fa3f76fb59bf77b7427588df294dcf1a15d88e497f8a8c3473edf",
    "7105a46cb4c2810f0c916e0bb4b4e4ef834ad42040c471b42c96d356a9fd1b21",
    "7e6578c2e34b53136741c6efe7799a2dce739651c22404a7894b48d42aa88b41",
    "309e31536dcf1556bb6c81b00cd992445b79ad8e89f9c0cd2a1f0675342538b3",
    "6228a5824a1e8d1554519125795ad14c1b7be681c6e9efbbbc66c91bbf2f89e5",
    "c92a057ef0c1c3dc5c81832facc21c436787ee806080fb64d9708c71cf4bb983",
    "6a62362c11e91c9f8205c47bbb30833a257c979f663b9a73d3c814ce228fe3dd",
    "c737e8142a927072977437977d3846acf36f5057d167cf45ea95c7423ed27a0f",
    "17a81fe310a349e035046198c2bac3b5d565a0958b5b3df084b139080ef42a0e",
})


def _normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def _digest(normalised: str) -> str:
    return hashlib.sha256(normalised.encode()).hexdigest()


def is_blocked_name(name: str) -> bool:
    return _digest(_normalise(name)) in BLOCKED_NAME_HASHES


def windows_of(text: str, max_words: int = 4):
    words = _normalise(text).split()
    for size in range(1, max_words + 1):
        for i in range(len(words) - size + 1):
            yield " ".join(words[i:i + size])
