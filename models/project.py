from pydantic import BaseModel, Field

BaseFields = {
    "id": Field(
        description="ID of the project",
        examples=[1],
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
}

class PostProjectRequestBody(BaseModel):
    name: str = BaseFields["name"]
    description: str | None = BaseFields["description"]

class UpdateProjectRequestBody(BaseModel):
    name: str = BaseFields["name"]
    description: str | None = BaseFields["description"]