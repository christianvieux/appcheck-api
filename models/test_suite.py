from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from models.smoke_tests import SmokeTestResponse


BaseFields = {
    "id": Field(
        description="ID of the test suite",
        examples=[1],
    ),
    "target_id": Field(
        description="ID of the target this suite belongs to",
        examples=[1],
    ),
    "name": Field(
        description="Name of the test suite",
        examples=["Health Checks"],
    ),
    "description": Field(
        default=None,
        description="Description of the test suite",
        examples=["Smoke tests for basic health endpoints"],
    ),
    "created_at": Field(
        description="When the test suite was created",
    ),
    "updated_at": Field(
        description="When the test suite was last updated",
    ),
}


class TestSuiteCreate(BaseModel):
    target_id: int = BaseFields["target_id"]
    name: str = BaseFields["name"]
    description: str | None = BaseFields["description"]


class TestSuiteUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TestSuiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = BaseFields["id"]
    target_id: int = BaseFields["target_id"]
    name: str = BaseFields["name"]
    description: str | None = BaseFields["description"]
    created_at: datetime = BaseFields["created_at"]
    updated_at: datetime = BaseFields["updated_at"]
    smoke_tests: list[SmokeTestResponse] = Field(default_factory=list)
