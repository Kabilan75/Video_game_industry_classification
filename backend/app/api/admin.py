"""
Admin API endpoints.
Provides administrative functions like triggering manual scrapes.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import ScraperRun
from logging_config import get_logger

router = APIRouter()
logger = get_logger("api")


@router.post("/scrape")
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger a scraping job.
    Runs in the background to avoid blocking the API.
    """
    logger.info("Manual scrape triggered by admin")
    
    # Create scraper run record
    scraper_run = ScraperRun(
        source_website="manual_trigger",
        status="queued"
    )
    db.add(scraper_run)
    db.commit()
    
    # Add background task (placeholder - will be implemented with actual scraper)
    # background_tasks.add_task(run_scraper, scraper_run.id)
    
    return {
        "message": "Scrape job queued successfully",
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
    from app.models import JobListing, Keyword, KeywordOccurrence
    from sqlalchemy import func
    
    total_jobs = db.query(func.count(JobListing.id)).filter(JobListing.is_active == 1).scalar()
    total_keywords = db.query(func.count(Keyword.id)).scalar()
    total_occurrences = db.query(func.count(KeywordOccurrence.id)).scalar()
    
    # Get last scrape time
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
