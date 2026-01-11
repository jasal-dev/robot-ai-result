from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Optional


#TEXT_EXTENSIONS = (".json", ".jsonl", ".txt", ".log", ".trace", ".network", ".stacks")
TEXT_EXTENSIONS = (".trace")


def find_single_trace_zip(trace_dir: str) -> Optional[str]:
    p = Path(trace_dir)
    if not p.exists():
        return None

    zips = sorted(p.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not zips:
        return None

    # Per your assumption: only one trace. If multiple, pick newest.
    return str(zips[0])


def extract_full_trace_text(
    trace_zip_path: str,
    max_total_chars: int = 160_000,
    max_file_chars: int = 100_000,
) -> str:
    """
    Extract "full trace" content as text by concatenating all text-like files
    inside the Playwright trace zip.

    Guards:
    - max_total_chars: total payload size (cost & token control)
    - max_file_chars: per-file cap in case one file is huge
    """
    out_parts: list[str] = []
    total = 0

    with zipfile.ZipFile(trace_zip_path, "r") as zf:
        names = zf.namelist()

        # Prefer deterministic ordering
        for name in sorted(names):
            lower = name.lower()

            # Only include text-ish files
            if not lower.endswith(TEXT_EXTENSIONS):
                continue

            try:
                raw = zf.read(name)
            except KeyError:
                continue

            text = raw.decode("utf-8", errors="replace")

            if len(text) > max_file_chars:
                text = text[:max_file_chars] + "\n<TRUNCATED_FILE>"

            block = f"\n===== TRACE FILE: {name} =====\n{text}\n"
            if total + len(block) > max_total_chars:
                remaining = max_total_chars - total
                if remaining <= 0:
                    out_parts.append("\n<TRACE_TRUNCATED_TOTAL>\n")
                    break
                out_parts.append(block[:remaining] + "\n<TRACE_TRUNCATED_TOTAL>\n")
                total = max_total_chars
                break

            out_parts.append(block)
            total += len(block)

    if not out_parts:
        return "No text-like trace files found in zip."
    return "".join(out_parts)
