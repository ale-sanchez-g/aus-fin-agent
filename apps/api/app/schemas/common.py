from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List
from datetime import datetime

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    mcp_mode: str
