"""
Admin API endpoints.
Provides administrative functions like triggering manual scrapes,
data quality reports, and system stats.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime

from app.database import get_db
from app.models import ScraperRun, JobListing, Keyword, KeywordOccurrence
from logging_config import get_logger
from app.services.scraper_service import run_all_uk_spiders

router = APIRouter()
logger = get_logger("api")


@router.post("/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger a scraping job (All UK Spiders).
    Runs in the background to avoid blocking the API.
    """
    logger.info("Manual scrape triggered by admin")

    scraper_run = ScraperRun(
        source_website="manual_trigger_uk_all",
        status="queued",
        start_time=datetime.now()
    )
    db.add(scraper_run)
    db.commit()
    db.refresh(scraper_run)

    background_tasks.add_task(run_all_uk_spiders, scraper_run.id)

    return {
        "message": "UK Scrape job queued successfully",
        "scraper_run_id": scraper_run.id,
        "status": "queued"
    }


@router.get("/scraper-status")
async def get_scraper_status(db: Session = Depends(get_db)):
    """
    Get status of recent scraper runs.
    """
    recent_runs = (
        db.query(ScraperRun)
        .order_by(ScraperRun.start_time.desc())
        .limit(10)
        .all()
    )

    runs = [
        {
            "id": run.id,
            "source_website": run.source_website,
            "start_time": run.start_time.isoformat() if run.start_time else None,
            "end_time": run.end_time.isoformat() if run.end_time else None,
            "jobs_scraped": run.jobs_scraped,
            "duplicates_found": run.duplicates_found,
            "errors_count": run.errors_count,
            "status": run.status
        }
        for run in recent_runs
    ]

    return {"recent_runs": runs}


@router.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Get overall system statistics.
    """
    total_jobs = db.query(func.count(JobListing.id)).filter(JobListing.is_active != 0).scalar()
    total_keywords = db.query(func.count(Keyword.id)).scalar()
    total_occurrences = db.query(func.count(KeywordOccurrence.id)).scalar()

    last_scrape = (
        db.query(ScraperRun)
        .filter(ScraperRun.status == "completed")
        .order_by(ScraperRun.end_time.desc())
        .first()
    )

    return {
        "total_active_jobs": total_jobs,
        "total_keywords": total_keywords,
        "total_keyword_occurrences": total_occurrences,
        "last_scrape_time": last_scrape.end_time.isoformat() if last_scrape and last_scrape.end_time else None
    }


@router.get("/data-quality")
async def get_data_quality_report(db: Session = Depends(get_db)):
    """
    Returns a data quality report:
    - Jobs with missing locations
    - Jobs with missing descriptions
    - Jobs with no keywords extracted
    - Duplicate location string variants
    """
    total = db.query(func.count(JobListing.id)).filter(JobListing.is_active != 0).scalar() or 0

    missing_location = db.query(func.count(JobListing.id)).filter(
        JobListing.is_active != 0,
        or_(JobListing.location == None, JobListing.location == "")
    ).scalar() or 0

    missing_description = db.query(func.count(JobListing.id)).filter(
        JobListing.is_active != 0,
        or_(JobListing.description == None, JobListing.description == "")
    ).scalar() or 0

    # Jobs with no keyword occurrences
    jobs_with_keywords = db.query(
        KeywordOccurrence.job_id.distinct()
    ).subquery()

    no_keywords = db.query(func.count(JobListing.id)).filter(
        JobListing.is_active != 0,
        ~JobListing.id.in_(
            db.query(KeywordOccurrence.job_id.distinct())
        )
    ).scalar() or 0

    # Location variants (raw unique locations)
    location_variants = db.query(
        JobListing.location,
        func.count(JobListing.id).label("count")
    ).filter(
        JobListing.is_active != 0,
        JobListing.location != None
    ).group_by(JobListing.location).order_by(
        func.count(JobListing.id).desc()
    ).limit(30).all()

    return {
        "total_active_jobs": total,
        "missing_location": missing_location,
        "missing_location_pct": round(missing_location / max(total, 1) * 100, 1),
        "missing_description": missing_description,
        "missing_description_pct": round(missing_description / max(total, 1) * 100, 1),
        "no_keywords_extracted": no_keywords,
        "no_keywords_pct": round(no_keywords / max(total, 1) * 100, 1),
        "location_variants": [
            {"location": r.location, "count": r.count} for r in location_variants
        ]
    }
