from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class ErrorResponse(BaseModel):
    code: str = Field(..., example="NOT_FOUND")
    message: str = Field(..., example="The requested resource was not found.")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int