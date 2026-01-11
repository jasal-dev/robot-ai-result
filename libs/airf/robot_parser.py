from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from robot.api import ExecutionResult


@dataclass
class FailureBundle:
    suite_name: str
    test_name: str
    status: str
    message: str
    # - last keywords
    # - screenshot paths
    # - tags
    # - elapsed time
    # - metadata


def extract_failures(output_xml_path: str, max_message_chars: int = 6000) -> list[FailureBundle]:
    result = ExecutionResult(output_xml_path)
    result.configure(stat_config={"suite_stat_level": 2, "tag_stat_combine": "tag"})

    failures: list[FailureBundle] = []

    # Walk all suites/tests
    for suite in result.suite.suites:
        failures.extend(_extract_suite_failures(suite, max_message_chars))

    # Also include root suite tests, if any
    failures.extend(_extract_suite_failures(result.suite, max_message_chars))

    # Deduplicate (root suite + nested may overlap depending on structure)
    unique = {}
    for f in failures:
        key = (f.suite_name, f.test_name)
        unique[key] = f
    return list(unique.values())


def _extract_suite_failures(suite, max_message_chars: int) -> list[FailureBundle]:
    out: list[FailureBundle] = []

    for test in suite.tests:
        if test.status != "FAIL":
            continue
        msg = (test.message or "").strip()
        if len(msg) > max_message_chars:
            msg = msg[:max_message_chars] + "\n<TRUNCATED>"
        out.append(
            FailureBundle(
                suite_name=suite.longname,
                test_name=test.name,
                status=test.status,
                message=msg,
            )
        )

    for subsuite in suite.suites:
        out.extend(_extract_suite_failures(subsuite, max_message_chars))

    return out
