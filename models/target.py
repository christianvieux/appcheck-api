from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from models.test_suite import TestSuiteResponse


class TargetType(str, Enum):
    web_app = "web_app"
    api = "api"
    mobile_app = "mobile_app"
    network = "network"


BaseFields = {
    "id": Field(
        description="ID of the target",
        examples=[1],
    ),
    "project_id": Field(
        description="ID of the project this target belongs to",
        examples=[1],
    ),
    "name": Field(
        description="Name of the target",
        examples=["Production API"],
    ),
    "url": Field(
        description="URL of the target",
        examples=["https://api.example.com"],
    ),
    "target_type": Field(
        description="Type of target",
        examples=["api"],
    ),
    "description": Field(
        default=None,
        description="Description of the target",
        examples=["Main production backend API"],
    ),
    "created_at": Field(
        description="When the target was created",
    ),
    "updated_at": Field(
        description="When the target was last updated",
    ),
}


class TargetCreate(BaseModel):
    project_id: int = BaseFields["project_id"]
    name: str = BaseFields["name"]
    url: HttpUrl = BaseFields["url"]
    target_type: TargetType = BaseFields["target_type"]
    description: str | None = BaseFields["description"]


class TargetUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    target_type: TargetType | None = None
    description: str | None = None


class TargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = BaseFields["id"]
    project_id: int = BaseFields["project_id"]
    name: str = BaseFields["name"]
    url: str = BaseFields["url"]
    target_type: TargetType = BaseFields["target_type"]
    description: str | None = BaseFields["description"]
    created_at: datetime = BaseFields["created_at"]
    updated_at: datetime = BaseFields["updated_at"]
    test_suites: list[TestSuiteResponse] = Field(default_factory=list)
