from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from datetime import datetime, timezone

from robot import run as robot_run

from libs.airf.openai import OpenAIFailureAnalyzer
from libs.airf.redact import redact_text
from libs.airf.robot_parser import extract_failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Robot Framework and analyze failures with AI.")
    parser.add_argument("--robot-args", nargs="*", default=["tests/"], help="Args passed to Robot Framework.")
    parser.add_argument("--outputdir", default="artifacts/robot", help="Robot output directory.")
    parser.add_argument("--ai-report", default="artifacts/ai_report.json", help="AI report output path.")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"), help="OpenAI API key.")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), help="OpenAI model name.")
    parser.add_argument("--max-failures", type=int, default=30, help="Max failures to analyze (cost control).")
    parser.add_argument("--max-message-chars", type=int, default=6000, help="Max chars from failure message.")
    args = parser.parse_args()

    outdir = pathlib.Path(args.outputdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Run Robot
    robot_rc = robot_run(
        *args.robot_args,
        outputdir=str(outdir),
        output="output.xml",
        log="log.html",
        report="report.html",
    )

    output_xml = outdir / "output.xml"
    if not output_xml.exists():
        print(f"ERROR: output.xml not found at {output_xml}", file=sys.stderr)
        return 2

    failures = extract_failures(str(output_xml), max_message_chars=args.max_message_chars)

    failures = failures[: args.max_failures]

    analyzer = OpenAIFailureAnalyzer(api_key=args.api_key, model=args.model)

    analyses = []
    for f in failures:
        bundle = {
            "suite_name": f.suite_name,
            "test_name": f.test_name,
            "status": f.status,
            "message": redact_text(f.message),
            # Add more context here later:
            # "build_id": os.getenv("BUILD_ID"),
            # "git_sha": os.getenv("GIT_SHA"),
            # "browser": os.getenv("BROWSER"),
        }

        try:
            analysis = analyzer.analyze(bundle)
            analyses.append(analysis.model_dump())
            print(f"[AI] {analysis.failure_type} ({analysis.confidence:.2f}) - {analysis.test_name}")
        except Exception as e:
            analyses.append(
                {
                    "test_name": f.test_name,
                    "suite_name": f.suite_name,
                    "failure_type": "unknown",
                    "confidence": 0.0,
                    "summary": "AI analysis failed",
                    "likely_root_cause": str(e),
                    "retry": {"should_retry": False, "reason": "AI error", "retry_scope": "none"},
                    "suggestions": [],
                    "tags_to_apply": [],
                    "missing_logs": [],
                }
            )
            print(f"[AI] ERROR analyzing {f.test_name}: {e}", file=sys.stderr)

    report_path = pathlib.Path(args.ai_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "robot_return_code": robot_rc,
        "robot_outputdir": str(outdir),
        "robot_output_xml": str(output_xml),
        "model": args.model,
        "failure_count_analyzed": len(analyses),
        "analyses": analyses,
    }

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote AI report: {report_path}")

    # Preserve original Robot return code semantics:
    return int(robot_rc)


if __name__ == "__main__":
    raise SystemExit(main())
