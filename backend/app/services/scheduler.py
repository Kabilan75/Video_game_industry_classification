
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.scraper_service import run_all_uk_spiders
from app.database import SessionLocal
from app.models import ScraperRun, JobListing, Keyword, KeywordOccurrence, RegionalSummary
from datetime import datetime
from sqlalchemy import func
import logging

logger = logging.getLogger("api")


def populate_regional_summary():
    """
    Refresh the pre-aggregated RegionalSummary table.
    Groups keyword occurrences by location and date (month granularity).
    Called automatically after each scheduled scrape.
    """
    logger.info("Populating RegionalSummary table...")
    db = SessionLocal()
    try:
        results = (
            db.query(
                JobListing.location,
                func.strftime("%Y-%m-01", JobListing.posting_date).label("period"),
                Keyword.id.label("keyword_id"),
                func.count(KeywordOccurrence.id).label("count")
            )
            .join(KeywordOccurrence, JobListing.id == KeywordOccurrence.job_id)
            .join(Keyword, KeywordOccurrence.keyword_id == Keyword.id)
            .filter(JobListing.is_active != 0)
            .filter(JobListing.location != None)
            .group_by(JobListing.location, "period", Keyword.id)
            .all()
        )

        upserted = 0
        for r in results:
            try:
                period_dt = datetime.strptime(r.period, "%Y-%m-%d") if r.period else None
                if not period_dt:
                    continue

                existing = db.query(RegionalSummary).filter_by(
                    region=r.location,
                    date=period_dt,
                    keyword_id=r.keyword_id
                ).first()

                if existing:
                    existing.count = r.count
                else:
                    db.add(RegionalSummary(
                        region=r.location,
                        date=period_dt,
                        keyword_id=r.keyword_id,
                        count=r.count
                    ))
                upserted += 1
            except Exception as row_err:
                logger.warning(f"Row error in regional summary: {row_err}")

        db.commit()
        logger.info(f"RegionalSummary populated: {upserted} rows upserted.")
    except Exception as e:
        logger.error(f"Failed to populate RegionalSummary: {e}")
        db.rollback()
    finally:
        db.close()


def scheduled_scrape_job():
    """
    Job to be run by the scheduler.
    Creates a DB record and triggers the scraping logic,
    then refreshes the RegionalSummary table.
    """
    logger.info("Starting scheduled daily scrape...")
    db = SessionLocal()
    try:
        scraper_run = ScraperRun(
            source_website="scheduled_daily_uk",
            status="queued",
            start_time=datetime.now()
        )
        db.add(scraper_run)
        db.commit()
        db.refresh(scraper_run)

        run_all_uk_spiders(scraper_run.id)

    except Exception as e:
        logger.error(f"Scheduled scrape failed to start: {e}")
    finally:
        db.close()

    # Refresh regional summary after scraping new data
    populate_regional_summary()


def start_scheduler():
    """
    Initialize and start the background scheduler.
    Runs daily scrape at 03:00 AM and regional summary refresh at 04:00 AM.
    """
    scheduler = BackgroundScheduler()

    # Main daily scrape
    scheduler.add_job(
        scheduled_scrape_job,
        CronTrigger(hour=3, minute=0),
        id="daily_uk_scrape",
        name="Daily UK Games Industry Scrape",
        replace_existing=True
    )

    # Standalone regional summary refresh (in case scrape already ran)
    scheduler.add_job(
        populate_regional_summary,
        CronTrigger(hour=4, minute=0),
        id="regional_summary_refresh",
        name="Regional Summary Refresh",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started. Daily scrape: 03:00 AM | Regional refresh: 04:00 AM.")
    return scheduler
