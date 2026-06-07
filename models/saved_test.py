from typing import Any, Optional
from pydantic import BaseModel, Field, PositiveInt, field_validator

from models.test_case import (
    HttpMethodAllowed,
    SingleAssertionModel,
)


class SavedTestCreate(BaseModel):
    suite_id: int
    target_id: int

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


class SavedTestUpdate(BaseModel):
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


class SavedTestResponse(BaseModel):
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

    class Config:
        from_attributes = True