"""
Keywords API endpoints.
Provides keyword analysis and frequency data.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from app.database import get_db
from app.models import Keyword, KeywordOccurrence, JobListing
from logging_config import get_logger

router = APIRouter()
logger = get_logger("api")


@router.get("/top")
async def get_top_keywords(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of keywords to return"),
    category: Optional[str] = Query(None, description="Filter by category (skill/software/experience)"),
    start_date: Optional[str] = Query(None, description="Start date for analysis"),
    end_date: Optional[str] = Query(None, description="End date for analysis"),
):
    """
    Get top N keywords by frequency across all jobs.
    """
    query = (
        db.query(
            Keyword.keyword,
            Keyword.category,
            func.sum(KeywordOccurrence.frequency).label("total_frequency"),
            func.count(KeywordOccurrence.job_id.distinct()).label("job_count")
        )
        .join(KeywordOccurrence)
        .join(JobListing)
    )
    
    # Apply category filter
    if category:
        query = query.filter(Keyword.category == category)
    
    # Apply date filters
    if start_date:
        query = query.filter(JobListing.posting_date >= start_date)
    
    if end_date:
        query = query.filter(JobListing.posting_date <= end_date)
    
    # Group and order
    results = (
        query
        .group_by(Keyword.id, Keyword.keyword, Keyword.category)
        .order_by(desc("total_frequency"))
        .limit(limit)
        .all()
    )
    
    keywords = [
        {
            "keyword": r.keyword,
            "category": r.category,
            "total_frequency": r.total_frequency,
            "job_count": r.job_count
        }
        for r in results
    ]
    
    logger.info(f"Retrieved top {len(keywords)} keywords (category={category})")
    
    return {"keywords": keywords}


@router.get("/{keyword}/jobs")
async def get_jobs_by_keyword(
    keyword: str,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get all jobs that contain a specific keyword.
    """
    keyword_obj = db.query(Keyword).filter(Keyword.keyword.ilike(keyword)).first()
    
    if not keyword_obj:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
    
    query = (
        db.query(JobListing)
        .join(KeywordOccurrence)
        .filter(KeywordOccurrence.keyword_id == keyword_obj.id)
        .filter(JobListing.is_active == 1)
    )
    
    total = query.count()
    offset = (page - 1) * page_size
    jobs = query.order_by(JobListing.posting_date.desc()).offset(offset).limit(page_size).all()
    
    return {
        "items": jobs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "keyword": keyword_obj.keyword,
        "category": keyword_obj.category
    }
