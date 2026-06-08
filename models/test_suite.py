from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class PostTestSuiteRequestBody(BaseModel):
    target_id: int
    name: str
    description: Optional[str] = None


class UpdateTestSuiteRequestBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TestResultResponse(BaseModel):
    id: int
    test_run_id: int
    saved_test_id: int
    target_id: int
    name: str | None = None
    status: Literal["passed", "failed"]
    status_code: int | None = None
    expected_status_code: int
    response_time_ms: int | None = None
    failure_message: str | None = None
    failure_details: list[str] = Field(default_factory=list)
    assertion_results: list[dict[str, Any]] | None = None
    created_at: datetime | None = None


class TestRunResponse(BaseModel):
    run_id: int
    suite_id: int
    suite_name: str
    status: Literal["passed", "failed"]
    total_tests: int
    passed_count: int
    failed_count: int
    duration_ms: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None


class TestRunDetailResponse(TestRunResponse):
    results: list[TestResultResponse] = Field(default_factory=list)
