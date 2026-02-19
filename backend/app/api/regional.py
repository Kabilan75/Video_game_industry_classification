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


@router.get("/heatmap")
async def get_skills_region_heatmap(
    db: Session = Depends(get_db),
    limit_regions: int = Query(8, ge=2, le=20, description="Number of top regions"),
    limit_keywords: int = Query(12, ge=2, le=30, description="Number of top keywords"),
    category: Optional[str] = Query(None, description="Filter by keyword category"),
):
    """
    Returns a skills × region heatmap matrix.
    Rows = top keywords, Columns = top regions, Cell values = job counts.
    This gives a true geographic view of skill demand across UK cities.
    """
    # 1. Get top regions by job count
    top_regions = (
        db.query(JobListing.location, func.count(JobListing.id).label("cnt"))
        .filter(JobListing.is_active == 1, JobListing.location != None, JobListing.location != "")
        .group_by(JobListing.location)
        .order_by(func.count(JobListing.id).desc())
        .limit(limit_regions)
        .all()
    )
    region_names = [r.location for r in top_regions]

    if not region_names:
        return {"regions": [], "keywords": [], "matrix": []}

    # 2. Get top keywords overall
    kw_query = (
        db.query(
            Keyword.keyword,
            func.count(KeywordOccurrence.job_id.distinct()).label("cnt")
        )
        .join(KeywordOccurrence)
    )
    if category:
        kw_query = kw_query.filter(Keyword.category == category)

    top_keywords = (
        kw_query
        .group_by(Keyword.id, Keyword.keyword)
        .order_by(func.count(KeywordOccurrence.job_id.distinct()).desc())
        .limit(limit_keywords)
        .all()
    )
    keyword_names = [k.keyword for k in top_keywords]

    if not keyword_names:
        return {"regions": region_names, "keywords": [], "matrix": []}

    # 3. Build the matrix: for each keyword × region, count distinct jobs
    raw = (
        db.query(
            Keyword.keyword,
            JobListing.location,
            func.count(KeywordOccurrence.job_id.distinct()).label("count")
        )
        .join(KeywordOccurrence, Keyword.id == KeywordOccurrence.keyword_id)
        .join(JobListing, KeywordOccurrence.job_id == JobListing.id)
        .filter(
            JobListing.is_active == 1,
            JobListing.location.in_(region_names),
            Keyword.keyword.in_(keyword_names),
        )
        .group_by(Keyword.keyword, JobListing.location)
        .all()
    )

    # Build lookup dict
    lookup = {}
    for r in raw:
        lookup[(r.keyword, r.location)] = r.count

    # 4. Assemble matrix rows (one per keyword)
    matrix = []
    for kw in keyword_names:
        row = {"keyword": kw}
        for region in region_names:
            row[region] = lookup.get((kw, region), 0)
        matrix.append(row)

    logger.info(f"Heatmap: {len(keyword_names)} keywords × {len(region_names)} regions")

    return {
        "regions": region_names,
        "keywords": keyword_names,
        "matrix": matrix
    }
