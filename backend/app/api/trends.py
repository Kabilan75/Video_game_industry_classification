"""
Trends API endpoints.
Provides time-series data for keyword demand analysis.
SQLite + PostgreSQL compatible.
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
    Uses strftime for SQLite compatibility (also works with PostgreSQL via SQLAlchemy).
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # SQLite-compatible date formatting
    fmt_map = {"day": "%Y-%m-%d", "week": "%Y-%W", "month": "%Y-%m"}
    date_format = fmt_map.get(interval, "%Y-%W")

    query = (
        db.query(
            func.strftime(date_format, JobListing.posting_date).label("period"),
            Keyword.keyword,
            Keyword.category,
            func.count(KeywordOccurrence.id).label("count")
        )
        .join(KeywordOccurrence, JobListing.id == KeywordOccurrence.job_id)
        .join(Keyword, KeywordOccurrence.keyword_id == Keyword.id)
        .filter(JobListing.posting_date >= start_date)
        .filter(JobListing.posting_date <= end_date)
    )

    if keyword:
        query = query.filter(Keyword.keyword.ilike(f"%{keyword}%"))
    if category:
        query = query.filter(Keyword.category == category)

    results = (
        query
        .group_by("period", Keyword.keyword, Keyword.category)
        .order_by("period")
        .all()
    )

    trends = {}
    for r in results:
        period_str = str(r.period) if r.period else "unknown"
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


@router.get("/jobs-over-time")
async def get_job_trends(
    db: Session = Depends(get_db),
    days: int = Query(90, ge=7, le=365, description="Number of days to analyze")
):
    """
    Get total number of jobs posted per day. SQLite-compatible.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    query = (
        db.query(
            func.strftime("%Y-%m-%d", JobListing.posting_date).label("date"),
            func.count(JobListing.id).label("count")
        )
        .filter(JobListing.posting_date >= start_date)
        .filter(JobListing.posting_date <= end_date)
        .group_by("date")
        .order_by("date")
        .all()
    )

    data = [{"date": row.date, "count": row.count} for row in query]
    return {"data": data}


@router.get("/emerging")
async def get_emerging_skills(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by category (skills/software/experience)"),
    limit: int = Query(10, ge=1, le=50, description="Number of results")
):
    """
    Identify emerging / fast-growing skills by comparing this week vs last week.
    Returns keywords sorted by growth rate (pct change over prior week).
    """
    now = datetime.now()
    this_week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)

    def keyword_counts(start, end):
        q = (
            db.query(
                Keyword.keyword,
                Keyword.category,
                func.count(KeywordOccurrence.id).label("count")
            )
            .join(KeywordOccurrence)
            .join(JobListing)
            .filter(JobListing.posting_date >= start)
            .filter(JobListing.posting_date < end)
        )
        if category:
            q = q.filter(Keyword.category == category)
        return {r.keyword: {"count": r.count, "category": r.category}
                for r in q.group_by(Keyword.id, Keyword.keyword, Keyword.category).all()}

    this_week = keyword_counts(this_week_start, now)
    last_week = keyword_counts(last_week_start, this_week_start)

    results = []
    for kw, data in this_week.items():
        prev = last_week.get(kw, {}).get("count", 0)
        curr = data["count"]
        if curr > 0:
            growth = round(((curr - prev) / max(prev, 1)) * 100, 1)
            results.append({
                "keyword": kw,
                "category": data["category"],
                "this_week": curr,
                "last_week": prev,
                "growth_pct": growth
            })

    results.sort(key=lambda x: x["growth_pct"], reverse=True)
    return {"emerging": results[:limit], "as_of": now.isoformat()}


@router.get("/experience-breakdown")
async def get_experience_breakdown(db: Session = Depends(get_db)):
    """
    Returns count of jobs per experience level keyword (Junior, Senior, Lead, etc.).
    """
    results = (
        db.query(
            Keyword.keyword,
            func.count(KeywordOccurrence.job_id.distinct()).label("job_count")
        )
        .join(KeywordOccurrence)
        .filter(Keyword.category == "experience")
        .group_by(Keyword.id, Keyword.keyword)
        .order_by(func.count(KeywordOccurrence.job_id.distinct()).desc())
        .all()
    )

    return {
        "breakdown": [{"level": r.keyword, "job_count": r.job_count} for r in results]
    }


@router.get("/dashboard-stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns current week vs last week delta stats for Dashboard change indicators.
    """
    now = datetime.now()
    this_week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)

    def count_jobs(start, end):
        return db.query(func.count(JobListing.id)).filter(
            JobListing.posting_date >= start,
            JobListing.posting_date < end
        ).scalar() or 0

    this_week_jobs = count_jobs(this_week_start, now)
    last_week_jobs = count_jobs(last_week_start, this_week_start)
    delta = this_week_jobs - last_week_jobs
    delta_pct = round((delta / max(last_week_jobs, 1)) * 100, 1)

    return {
        "this_week_jobs": this_week_jobs,
        "last_week_jobs": last_week_jobs,
        "delta": delta,
        "delta_pct": delta_pct,
        "trend": "up" if delta > 0 else ("down" if delta < 0 else "flat")
    }
