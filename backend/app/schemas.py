"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Any, Generic, TypeVar

T = TypeVar('T')

class JobListingBase(BaseModel):
    """Base job listing schema."""
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[str] = None
    posting_date: Optional[datetime] = None
    url: str
    source_website: str


class JobListingResponse(JobListingBase):
    """Job listing response schema."""
    id: int
    scraped_date: datetime
    is_active: int
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: Optional[int] = None


class KeywordResponse(BaseModel):
    """Keyword response schema."""
    keyword: str
    category: str
    total_frequency: int
    job_count: int
