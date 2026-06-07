from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class TargetType(str, Enum):
    web = "web"
    api = "api"
    mobile = "mobile"
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
        examples=["Main Website"],
    ),
    "url": Field(
        description="URL of the target",
        examples=["https://example.com"],
    ),
    "target_type": Field(
        description="Type of target",
        examples=["web"],
    ),
}


class PostTargetRequestBody(BaseModel):
    project_id: int = BaseFields["project_id"]
    name: str = BaseFields["name"]
    url: HttpUrl = BaseFields["url"]
    target_type: TargetType = BaseFields["target_type"]


class UpdateTargetRequestBody(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    target_type: TargetType | None = None


class TargetResponse(BaseModel):
    id: int = BaseFields["id"]
    project_id: int = BaseFields["project_id"]
    name: str = BaseFields["name"]
    url: str = BaseFields["url"]
    target_type: TargetType = BaseFields["target_type"]

    class Config:
        from_attributes = True
