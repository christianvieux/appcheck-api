from typing import Any, Literal
from pydantic import BaseModel, AnyUrl, PositiveInt, Field, field_validator, model_validator
from enum import StrEnum


HttpMethodAllowed     = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
NestedOperatorAllowed = Literal["every_item_matches", "some_item_matches"]
SimpleOperatorAllowed = Literal[
    "equals",
    "not_equals",
    "exists",
    "is_number",
    "is_string",
    "is_boolean",
    "is_array",
    "is_object",
    "greater_than",
    "less_than",
    "contains",
]

OPERATORS_THAT_NEED_VALUE = {
    "equals", 
    "not_equals", 
    "greater_than", 
    "less_than", 
    "contains"
}

AssertionOperatorAllowed = SimpleOperatorAllowed | NestedOperatorAllowed



class RuleItemModel(BaseModel):
    path: str | None = Field(
        None,
        description="JSON path in dot form. Leave empty to check the whole item.",
        examples=["data.user.role"],
    )

    operator: SimpleOperatorAllowed = Field(
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
        if self.operator in OPERATORS_THAT_NEED_VALUE and "value" not in self.model_fields_set:
            raise ValueError(f"Operator '{self.operator}' requires a value. in rule with path '{self.path}'")

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

    operator: AssertionOperatorAllowed = Field(
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
        if self.operator in OPERATORS_THAT_NEED_VALUE and "value" not in self.model_fields_set:
            raise ValueError(f"Operator '{self.operator}' requires a value.")

        if self.operator in {"every_item_matches", "some_item_matches"} and not self.conditions:
            raise ValueError(f"Operator '{self.operator}' requires conditions.")

        return self


class SingleTestCaseRequest(BaseModel):
    name: str = Field(
        ...,
        description="Name of the test case",
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

    # This allows flexibility in how users specify the HTTP method (e.g., "get", "GET", "Get") and normalizes it to uppercase
    @field_validator("method", mode="before")
    @classmethod
    def normalize_method(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value


class RunTestsRequest(BaseModel):
    test_cases: list[SingleTestCaseRequest] = Field(
        ...,
        description="List of test cases to run",
    )


class SingleTestCaseResult(BaseModel):
    name: str = Field(
        ...,
        description="Name of the test case",
        examples=["Get user by ID"],
    )

    status: Literal["passed", "failed"] = Field(
        ...,
        description="Result status of the test case",
        examples=["passed"],
    )

    failure_details: list[str] = Field(
        default_factory=list,
        description="List of failure messages if the test failed",
        examples=[["Expected status code 200, got 404"]],
    )