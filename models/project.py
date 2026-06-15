from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

BaseFields = {
    "id": Field(
        description="ID of the project",
        examples=[1],
    ),
     "owner_id": Field(
        default=None,
        description="ID of the user who owns the project",
        examples=["user_123"],
    ),
    "name": Field(
        description="Name of the project",
        examples=["My Awesome Project"],
    ),
    "description": Field(
        default=None,
        description="Description of the project",
        examples=["This project is about..."],
    ),
    "created_at": Field(
        description="When the project was created",
    ),
    "updated_at": Field(
        description="When the project was last updated",
    ),
}

class ProjectCreate(BaseModel):
    name: str = BaseFields["name"]
    description: str | None = BaseFields["description"]

class ProjectUpdate(BaseModel):
    name: str = BaseFields["name"]
    description: str | None = BaseFields["description"]

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = BaseFields["id"]
    owner_id: str | None = BaseFields["owner_id"]
    name: str = BaseFields["name"]
    description: str | None = BaseFields["description"]
    created_at: datetime = BaseFields["created_at"]
    updated_at: datetime = BaseFields["updated_at"]