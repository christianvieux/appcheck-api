from typing import Any, Literal, Optional
from pydantic import BaseModel, AnyUrl, ConfigDict, PositiveInt, Field, field_validator, model_validator

from models.assertions import (
    AssertionOperator,
    operator_allowed_in_rules,
    operator_requires_conditions,
    operator_requires_value,
)
from models.smoke_test_run_result import RunSource, TriggeredBy

HttpMethodAllowed     = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


class RuleItemModel(BaseModel):
    path: str | None = Field(
        None,
        description="JSON path in dot form. Leave empty to check the whole item.",
        examples=["data.user.role"],
    )

    operator: AssertionOperator = Field(
        ...,
        description="The operator to use for this rule.",
        examples=["equals"],
    )

    value: Any | None = Field(
        None,
        description="The value to compare when needed.",
        examples=["admin"],
    )

    @model_validator(mode="after")
    def validate_operator_requirements(self):
        if not operator_allowed_in_rules(self.operator):
            raise ValueError(f"Operator '{self.operator.value}' cannot be used in nested rules.")

        if operator_requires_value(self.operator) and "value" not in self.model_fields_set:
            raise ValueError(f"Operator '{self.operator.value}' requires a value. in rule with path '{self.path}'")

        return self

class SingleAssertionModel(BaseModel):
    type: Literal["json_body"] = Field(
        ...,
        description="Type of assertion to run.",
        examples=["json_body"],
    )

    path: str | None = Field(
        None,
        description="JSON path in dot form. Leave empty to check the whole body.",
        examples=["data.user.id"],
    )

    operator: AssertionOperator = Field(
        ...,
        description="The operator to use for this assertion.",
        examples=["equals"],
    )

    value: Any | None = Field(
        None,
        description="The value to compare when needed.",
        examples=[123],
    )

    conditions: list[RuleItemModel] = Field(
        default_factory=list,
        description="Optional rules to pass before this assertion runs.",
    )

    @model_validator(mode="after")
    def validate_operator_requirements(self):
        if operator_requires_value(self.operator) and "value" not in self.model_fields_set:
            raise ValueError(f"Operator '{self.operator.value}' requires a value.")

        if operator_requires_conditions(self.operator) and not self.conditions:
            raise ValueError(f"Operator '{self.operator.value}' requires conditions.")

        return self

class SingleSmokeTestRequest(BaseModel):
    name: str = Field(
        ...,
        description="Name of the smoke test",
        examples=["Get user by ID"],
    )

    url: AnyUrl = Field(
        ...,
        description="URL to send the request to",
        examples=["https://jsonplaceholder.typicode.com/users/1"],
    )

    method: HttpMethodAllowed = Field(
        ...,
        description="HTTP method to use",
        examples=["GET"],
    )

    expected_status_code: int = Field(
        ...,
        gt=99,
        lt=600,
        description="Expected HTTP status code",
        examples=[200],
    )

    max_response_time_ms: PositiveInt = Field(
        30000,
        description="Maximum allowed response time in milliseconds. Default is 30000 ms (30 seconds).",
        examples=[30000],
    )

    assertions: list[SingleAssertionModel] = Field(
        default_factory=list,
        description="Assertions to run against the response",
    )

    headers: dict[str, str] | None = Field(
        None,
        description="Optional headers to include in the request",
        examples=[{"Authorization": "Bearer token123"}],
    )

    body: dict | None = Field(
        None,
        description="Optional JSON body to include in the request (for POST, PUT, PATCH)",
        examples=[{"name": "John", "age": 30}],
    )

    query_params: dict[str, str] | None = Field(
        None,
        description="Optional query parameters to include in the URL",
        examples=[{"page": "1", "limit": "10"}],
    )

    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value

class RunSmokeTestsRequest(BaseModel):
    smoke_tests: list[SingleSmokeTestRequest] = Field(
        ...,
        description="List of smoke tests to run",
    )


class RunSavedSmokeTestsRequest(BaseModel):
    smoke_test_ids: list[PositiveInt] = Field(
        ...,
        min_length=1,
        description="Saved smoke test IDs to run for the authenticated user.",
        examples=[[1, 2, 3]],
    )

    run_source: RunSource = Field(
        ...,
        description="What triggered the run group.",
        examples=["suite"],
    )

    triggered_by: TriggeredBy = Field(
        "manual",
        description="Who or what initiated the run.",
        examples=["manual"],
    )


class RunSavedSingleSmokeTestRequest(BaseModel):
    smoke_test_id: PositiveInt = Field(
        ...,
        description="Saved smoke test ID to run for the authenticated user.",
        examples=[1],
    )

    run_source: RunSource = Field(
        ...,
        description="What triggered the run.",
        examples=["single"],
    )

    run_group_id: str | None = Field(
        None,
        description="Optional run group ID to associate this single run with.",
        examples=["manual-check-2026-06-15"],
    )

    triggered_by: TriggeredBy = Field(
        "manual",
        description="Who or what initiated the run.",
        examples=["manual"],
    )

class SingleSmokeTestResult(BaseModel):
    name: str = Field(
        ...,
        description="Name of the smoke test",
        examples=["Get user by ID"],
    )

    status: Literal["passed", "failed"] = Field(
        ...,
        description="Result status of the smoke test",
        examples=["passed"],
    )

    response: dict[str, Any] | None = None

    response_time_ms: int | None = None

    failure_details: list[str] = Field(
        default_factory=list,
        description="List of failure messages if the smoke test failed",
        examples=[["Expected status code 200, got 404"]],
    )

class SmokeTestCreate(BaseModel):
    suite_id: int
    target_id: int | None = None

    name: str
    description: Optional[str] = None

    method: HttpMethodAllowed
    path: str = Field(
        ...,
        description="Relative path for the target, like /health or /api/users"
    )

    headers: dict[str, str] | None = None
    query_params: dict[str, str] | None = None
    body: dict[str, Any] | None = None

    expected_status: int = Field(..., gt=99, lt=600)
    max_response_time_ms: PositiveInt = 30000

    assertions: list[SingleAssertionModel] = Field(default_factory=list)

    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("path")
    @classmethod
    def validate_path(cls, value):
        if not value.startswith("/"):
            raise ValueError("Path must start with '/'. Example: /health")
        return value

class SmokeTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    method: Optional[HttpMethodAllowed] = None
    path: Optional[str] = None

    headers: Optional[dict[str, str]] = None
    query_params: Optional[dict[str, str]] = None
    body: Optional[dict[str, Any]] = None

    expected_status: Optional[int] = Field(None, gt=99, lt=600)
    max_response_time_ms: Optional[PositiveInt] = None

    assertions: Optional[list[SingleAssertionModel]] = None

    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("path")
    @classmethod
    def validate_path(cls, value):
        if value is not None and not value.startswith("/"):
            raise ValueError("Path must start with '/'. Example: /health")
        return value

class SmokeTestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suite_id: int
    target_id: int

    name: str
    description: Optional[str] = None

    method: str
    path: str

    headers: dict[str, str] | None = None
    query_params: dict[str, str] | None = None
    body: dict[str, Any] | None = None

    expected_status: int
    max_response_time_ms: int

    assertions: list[dict[str, Any]] | None = None
