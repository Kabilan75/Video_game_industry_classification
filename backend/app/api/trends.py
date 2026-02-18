"""
Trends API endpoints.
Provides time-series data for keyword demand analysis.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models import Keyword, KeywordOccurrence, JobListing
from logging_config import get_logger

router = APIRouter()
logger = get_logger("api")


@router.get("")
async def get_trends(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, description="Specific keyword to track"),
    category: Optional[str] = Query(None, description="Category to track"),
    days: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    interval: str = Query("week", description="Time interval (day/week/month)")
):
    """
    Get time-series data showing keyword demand trends over time.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = (
        db.query(
            func.date_trunc(interval, JobListing.posting_date).label("period"),
            Keyword.keyword,
            Keyword.category,
            func.count(KeywordOccurrence.id).label("count")
        )
        .join(KeywordOccurrence, JobListing.id == KeywordOccurrence.job_id)
        .join(Keyword, KeywordOccurrence.keyword_id == Keyword.id)
        .filter(JobListing.posting_date >= start_date)
        .filter(JobListing.posting_date <= end_date)
    )
    
    # Apply filters
    if keyword:
        query = query.filter(Keyword.keyword.ilike(f"%{keyword}%"))
    
    if category:
        query = query.filter(Keyword.category == category)
    
    # Group by period and keyword
    results = (
        query
        .group_by("period", Keyword.keyword, Keyword.category)
        .order_by("period")
        .all()
    )
    
    # Format response
    trends = {}
    for r in results:
        period_str = r.period.strftime("%Y-%m-%d")
        if period_str not in trends:
            trends[period_str] = []
        
        trends[period_str].append({
            "keyword": r.keyword,
            "category": r.category,
            "count": r.count
        })
    
    logger.info(f"Retrieved trends for {len(results)} data points (days={days}, interval={interval})")
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "interval": interval,
        "trends": trends
    }
