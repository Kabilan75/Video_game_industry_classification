"""
Jobs API endpoints.
Provides job listing queries with filtering and pagination.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models import JobListing
from app.schemas import JobListingResponse, PaginatedResponse
from logging_config import get_logger

router = APIRouter()
logger = get_logger("api")


@router.get("", response_model=PaginatedResponse[JobListingResponse])
async def get_jobs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    location: Optional[str] = Query(None, description="Filter by location"),
    company: Optional[str] = Query(None, description="Filter by company"),
    keyword: Optional[str] = Query(None, description="Filter by keyword in title/description"),
    start_date: Optional[datetime] = Query(None, description="Filter jobs posted after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter jobs posted before this date"),
):
    """
    Get paginated list of job listings with optional filters.
    """
    query = db.query(JobListing).filter(JobListing.is_active == 1)
    
    # Apply filters
    if location:
        query = query.filter(JobListing.location.ilike(f"%{location}%"))
    
    if company:
        query = query.filter(JobListing.company.ilike(f"%{company}%"))
    
    if keyword:
        query = query.filter(
            (JobListing.title.ilike(f"%{keyword}%")) |
            (JobListing.description.ilike(f"%{keyword}%"))
        )
    
    if start_date:
        query = query.filter(JobListing.posting_date >= start_date)
    
    if end_date:
        query = query.filter(JobListing.posting_date <= end_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    jobs = query.order_by(JobListing.posting_date.desc()).offset(offset).limit(page_size).all()
    
    logger.info(f"Retrieved {len(jobs)} jobs (page {page}, filters: location={location}, company={company})")
    
    return {
        "items": jobs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{job_id}", response_model=JobListingResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific job listing by ID.
    """
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    
    if not job:
        logger.warning(f"Job {job_id} not found")
        return {"detail": "Job not found"}
    
    return job
