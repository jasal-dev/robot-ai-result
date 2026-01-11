from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Literal


FailureType = Literal[
    "application_bug",
    "test_bug",
    "environment_issue",
    "flaky_test",
    "test_data_issue",
    "unknown",
]

SuggestionCategory = Literal[
    "selector",
    "data_setup",
    "timing",
    "data",
    "assertion",
    "infra",
    "auth",
    "other",
]

RetryScope = Literal["test", "suite", "none"]


class RetryDecision(BaseModel):
    should_retry: bool
    reason: str
    retry_scope: RetryScope = "test"


class FixSuggestion(BaseModel):
    category: SuggestionCategory
    suggestion: str


class FailureAnalysis(BaseModel):
    test_name: str
    suite_name: str
    failure_type: FailureType
    confidence: float = Field(ge=0, le=1)
    summary: str
    likely_root_cause: str
    retry: RetryDecision
    suggestions: List[FixSuggestion] = []
    tags_to_apply: List[str] = []
    missing_logs: List[str] = []
