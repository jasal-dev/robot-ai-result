from __future__ import annotations

import re
from typing import Iterable


SECRET_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?i)(api[_-]?key)\s*[:=]\s*([A-Za-z0-9_\-]+)"), r"\1=<REDACTED>"),
    (re.compile(r"(?i)(authorization:\s*bearer)\s+[A-Za-z0-9\.\-_]+"), r"\1 <REDACTED>"),
    (re.compile(r"(?i)(password)\s*[:=]\s*([^\s]+)"), r"\1=<REDACTED>"),
    (re.compile(r"(?i)(token)\s*[:=]\s*([A-Za-z0-9\.\-_]+)"), r"\1=<REDACTED>"),
]


def redact_text(text: str) -> str:
    if not text:
        return text
    out = text
    for pat, repl in SECRET_PATTERNS:
        out = pat.sub(repl, out)
    return out


def tail_lines(lines: Iterable[str], max_lines: int) -> list[str]:
    arr = list(lines)
    if len(arr) <= max_lines:
        return arr
    return arr[-max_lines:]
