from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RunSource = Literal["single", "suite", "target", "project", "monitor"]
TriggeredBy = Literal["manual", "monitor", "api"]
RunStatus = Literal["passed", "failed"]


class SmokeTestRunResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_group_id: str
    owner_id: str
    smoke_test_id: int
    project_id: int
    suite_id: int
    target_id: int
    run_source: RunSource
    triggered_by: TriggeredBy

    name_snapshot: str
    method_snapshot: str
    url_snapshot: str
    path_snapshot: str
    expected_status_snapshot: int
    max_response_time_ms_snapshot: int
    assertions_snapshot: list[dict[str, Any]] | None = None
    headers_snapshot: dict[str, str] | None = None
    query_params_snapshot: dict[str, str] | None = None
    body_snapshot: dict[str, Any] | None = None

    status: RunStatus
    status_code: int | None = None
    response_time_ms: int | None = None
    failure_message: str | None = None
    failure_details: list[str] | None = Field(default_factory=list)
    assertion_results: list[dict[str, Any]] | None = Field(default_factory=list)

    started_at: datetime
    finished_at: datetime
    created_at: datetime | None = None


class SmokeTestRunGroupSummaryResponse(BaseModel):
    run_group_id: str
    run_source: RunSource
    triggered_by: TriggeredBy
    status: RunStatus
    total_tests: int
    passed_count: int
    failed_count: int
    duration_ms: int
    project_ids: list[int] = Field(default_factory=list)
    suite_ids: list[int] = Field(default_factory=list)
    target_ids: list[int] = Field(default_factory=list)
    started_at: datetime
    finished_at: datetime
    created_at: datetime | None = None


class SmokeTestRunGroupResponse(SmokeTestRunGroupSummaryResponse):
    message: str | None = None
    test_results: list[SmokeTestRunResultResponse] = Field(default_factory=list)
