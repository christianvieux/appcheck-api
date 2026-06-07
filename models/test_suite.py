from typing import Optional
from pydantic import BaseModel


class PostTestSuiteRequestBody(BaseModel):
    target_id: int
    name: str
    description: Optional[str] = None


class UpdateTestSuiteRequestBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None