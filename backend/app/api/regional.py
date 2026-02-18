"""
Regional analysis API endpoints.
Provides geographic distribution of jobs and keywords.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.database import get_db
from app.models import JobListing, Keyword, KeywordOccurrence
from logging_config import get_logger

router = APIRouter()
logger = get_logger("api")


@router.get("/distribution")
async def get_regional_distribution(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, description="Filter by specific keyword"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get job distribution across UK regions.
    Returns count of jobs per region (location field).
    """
    query = db.query(
        JobListing.location,
        func.count(JobListing.id).label("job_count")
    ).filter(JobListing.is_active == 1)
    
    # Join with keywords if filtering
    if keyword or category:
        query = (
            query
            .join(KeywordOccurrence, JobListing.id == KeywordOccurrence.job_id)
            .join(Keyword, KeywordOccurrence.keyword_id == Keyword.id)
        )
        
        if keyword:
            query = query.filter(Keyword.keyword.ilike(f"%{keyword}%"))
        
        if category:
            query = query.filter(Keyword.category == category)
    
    results = (
        query
        .group_by(JobListing.location)
        .order_by(func.count(JobListing.id).desc())
        .all()
    )
    
    distribution = [
        {
            "region": r.location or "Unknown",
            "job_count": r.job_count
        }
        for r in results
    ]
    
    logger.info(f"Retrieved regional distribution for {len(distribution)} regions")
    
    return {"distribution": distribution}


@router.get("/compare")
async def compare_regions(
    db: Session = Depends(get_db),
    regions: str = Query(..., description="Comma-separated list of regions to compare"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
):
    """
    Compare keyword demand across specified regions.
    """
    region_list = [r.strip() for r in regions.split(",")]
    
    query = (
        db.query(
            JobListing.location,
            Keyword.keyword,
            Keyword.category,
            func.count(KeywordOccurrence.id).label("count")
        )
        .join(KeywordOccurrence, JobListing.id == KeywordOccurrence.job_id)
        .join(Keyword, KeywordOccurrence.keyword_id == Keyword.id)
        .filter(JobListing.is_active == 1)
    )
    
    # Filter by regions (case-insensitive partial match)
    region_filters = [JobListing.location.ilike(f"%{r}%") for r in region_list]
    query = query.filter(func.or_(*region_filters))
    
    if keyword:
        query = query.filter(Keyword.keyword.ilike(f"%{keyword}%"))
    
    results = (
        query
        .group_by(JobListing.location, Keyword.keyword, Keyword.category)
        .order_by(JobListing.location, func.count(KeywordOccurrence.id).desc())
        .all()
    )
    
    # Organize by region
    comparison = {}
    for r in results:
        region = r.location or "Unknown"
        if region not in comparison:
            comparison[region] = []
        
        comparison[region].append({
            "keyword": r.keyword,
            "category": r.category,
            "count": r.count
        })
    
    logger.info(f"Compared {len(region_list)} regions with {len(results)} keyword matches")
    
    return {
        "regions": region_list,
        "comparison": comparison
    }
