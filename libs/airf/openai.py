from __future__ import annotations

import json
from typing import Any, Optional

from openai import OpenAI
from pydantic import ValidationError

from libs.airf.models import FailureAnalysis
from libs.airf.prompt import SYSTEM_PROMPT, build_user_prompt


class OpenAIFailureAnalyzer:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4.1-mini",
        timeout_s: float = 30.0,
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.timeout_s = timeout_s

    def analyze(self, failure_bundle: dict) -> FailureAnalysis:
        schema = FailureAnalysis.model_json_schema()

        resp = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(failure_bundle)},
            ],
            text_format=FailureAnalysis,
        )

        # The SDK returns structured outputs as text in most cases; parse defensively.
        text = resp.output_text
        try:
            return FailureAnalysis.model_validate_json(text)
        except ValidationError as e:
            # If strict schema is supported, this should be rare, but keep it safe.
            raise RuntimeError(f"AI returned invalid structured output: {e}\nRaw:\n{text}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"AI returned non-JSON output.\nRaw:\n{text}") from e
