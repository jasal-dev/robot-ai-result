# robot-ai-result

Turn failing Robot Framework runs into actionable triage reports in one command.  
This project executes your Robot suite, extracts failed tests, adds Playwright trace context (when available), and generates structured AI analysis with likely root cause, retry guidance, and fix suggestions.

## Why use this

- **Faster failure triage**: converts long failure logs into concise root-cause summaries.
- **Structured output**: AI results are emitted as JSON, ready for CI pipelines or dashboards.
- **Playwright-aware analysis**: includes trace evidence from `robotframework-browser` runs.
- **Cost control**: limits analyzed failures and truncates oversized messages/traces.

## Features

- Runs Robot Framework tests and preserves standard artifacts:
	- `output.xml`
	- `log.html`
	- `report.html`
- Parses failed tests from Robot results.
- Redacts common secrets from failure messages before AI processing.
- Finds the newest Playwright trace zip (if present) and includes extracted trace text.
- Calls OpenAI with structured response parsing into a typed schema.
- Produces a machine-readable AI report containing:
	- failure classification (`application_bug`, `test_bug`, `flaky_test`, etc.)
	- confidence score
	- summary + likely root cause
	- retry decision and scope
	- categorized fix suggestions
	- tags and missing-log hints

## Requirements

- Python 3.10+
- An OpenAI API key
- Dependencies listed in `requirements.txt`

## Installation

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Set your API key:

```powershell
$env:OPENAI_API_KEY="your_key_here"
```

Optional model override:

```powershell
$env:OPENAI_MODEL="gpt-4.1-mini"
```

## Quick start

Run the default suite (`tests/`) and generate AI analysis:

```bash
python run.py --robot-args tests/
```

After execution, you should see:

- `artifacts/robot/output.xml`
- `artifacts/robot/log.html`
- `artifacts/robot/report.html`
- `artifacts/ai_report.json`
- `artifacts/ai_debug_payload.json` (last payload sent for AI analysis)

## Command-line usage

```bash
python run.py [options]
```

### Options

- `--robot-args ...` (default: `tests/`)
	- Arguments passed directly to Robot Framework.
- `--outputdir` (default: `artifacts/robot`)
	- Robot output directory.
- `--ai-report` (default: `artifacts/ai_report.json`)
	- Path to final AI report JSON.
- `--api-key` (default: `OPENAI_API_KEY` env var)
	- OpenAI API key.
- `--model` (default: `OPENAI_MODEL` env var or `gpt-4.1-mini`)
	- Model used for analysis.
- `--max-failures` (default: `30`)
	- Maximum failed tests analyzed by AI.
- `--max-message-chars` (default: `6000`)
	- Maximum failure message length before truncation.

## Example commands

Run a specific suite file:

```bash
python run.py --robot-args tests/sauce.robot
```

Use a custom output directory and report path:

```bash
python run.py --outputdir artifacts/robot --ai-report ai-reports/ai_report.json --robot-args tests/
```

Analyze with a different model:

```bash
python run.py --model gpt-4.1-mini --robot-args tests/
```

## How it works

1. Run Robot Framework with the provided args.
2. Parse `output.xml` and collect failed tests.
3. Detect the newest Playwright trace zip under `artifacts/robot/browser/traces`.
4. Extract trace text (`.trace` files) with payload limits.
5. Redact sensitive tokens from failure message text.
6. Send bundled context to OpenAI for structured analysis.
7. Write a consolidated JSON report.

## AI report format

Top-level fields in `artifacts/ai_report.json`:

- `generated_at`
- `robot_return_code`
- `robot_outputdir`
- `robot_output_xml`
- `model`
- `failure_count_analyzed`
- `analyses` (array)

Each `analyses[]` item includes:

- `test_name`, `suite_name`
- `failure_type`, `confidence`
- `summary`, `likely_root_cause`
- `retry` (`should_retry`, `reason`, `retry_scope`)
- `suggestions[]` (`category`, `suggestion`)
- `tags_to_apply[]`
- `missing_logs[]`

## Repository layout

```text
.
├── run.py                       # Main entrypoint
├── requirements.txt
├── tests/                       # Example Robot tests
├── libs/airf/
│   ├── models.py                # Structured AI schema
│   ├── openai.py                # OpenAI client + parsing
│   ├── prompt.py                # Prompt construction
│   ├── robot_parser.py          # Robot failure extraction
│   ├── pw_trace_full.py         # Playwright trace discovery/extraction
│   └── redact.py                # Basic secret redaction
├── artifacts/                   # Runtime outputs
└── ai-reports/                  # Sample generated reports
```

## Troubleshooting

- **`output.xml not found`**
	- Verify Robot executed successfully and `--outputdir` is correct.
- **No trace context in analysis**
	- Ensure Browser library tracing is enabled and a trace zip exists under `artifacts/robot/browser/traces`.
- **AI analysis errors**
	- Confirm `OPENAI_API_KEY` is set and valid.
	- Try a valid model via `--model`.
- **Large/expensive runs**
	- Lower `--max-failures` and/or `--max-message-chars`.

## Notes

- The script returns Robot Framework’s return code (CI-friendly behavior).
- If AI analysis fails for a test, a fallback `unknown` analysis record is written so the report remains complete.

## Next ideas

- Add CI pipeline examples (GitHub Actions/Azure DevOps).
- Add richer context (screenshots, last keywords, environment metadata).
- Export markdown or HTML triage summaries from the JSON report.