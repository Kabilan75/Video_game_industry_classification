
import subprocess
import os
import sys
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import ScraperRun
from app.database import SessionLocal

logger = logging.getLogger("api")

# Path to the scraper directory (relative to this file)
# backend/app/services/scraper_service.py -> backend/app/services -> backend/app -> backend -> root -> scraper
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRAPER_DIR = os.path.join(os.path.dirname(BASE_DIR), "scraper")


def run_spider(spider_name: str, run_id: int):
    """
    Run a specific spider using subprocess.
    """
    logger.info(f"Starting spider: {spider_name} (Run ID: {run_id})")
    
    # Ensure we use the same Python interpreter
    python_exe = sys.executable
    
    try:
        # Run scrapy crawl
        # We assume the scraper directory has scrapy.cfg
        result = subprocess.run(
            [python_exe, "-m", "scrapy", "crawl", spider_name, "-s", "LOG_LEVEL=INFO"],
            cwd=SCRAPER_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Spider {spider_name} finished successfully.")
        return True, result.stdout
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Spider {spider_name} failed: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        logger.error(f"Error running spider {spider_name}: {str(e)}")
        return False, str(e)


def run_all_uk_spiders(run_id: int):
    """
    Sequentially run all 4 UK spiders.
    This function is intended to be run in a background thread/task.
    """
    spiders = [
        "games_jobs_direct",         # Priority 1: Major aggregator
        "aardvark_swift",            # Priority 2: Specialist recruiter
        "gamesindustry_london",      # Priority 3: GI.biz London
        "hitmarker_london",          # Priority 4: Hitmarker London
        "workwithindies_london",     # Priority 5: Indie London
        "gamesindustry_uk",          # General UK
        "gamesindustry_scotland",
        "gamesindustry_midlands"
    ]
    
    db = SessionLocal()
    try:
        scraper_run = db.query(ScraperRun).get(run_id)
        if not scraper_run:
            logger.error(f"Scraper run {run_id} not found!")
            return

        scraper_run.status = "running"
        scraper_run.start_time = datetime.now()
        db.commit()

        success_count = 0
        total_output = ""

        for spider in spiders:
            success, output = run_spider(spider, run_id)
            if success:
                success_count += 1
            total_output += f"\n--- {spider} ---\n{output}\n"

        # Update run status
        scraper_run.end_time = datetime.now()
        if success_count == len(spiders):
            scraper_run.status = "completed"
        elif success_count > 0:
            scraper_run.status = "partial_success"
        else:
            scraper_run.status = "failed"
            
        # We could parse output to get job counts, or rely on distinct counting in DB
        # For now, we'll verify via DB stats later
        
        db.commit()
        logger.info(f"Scraper run {run_id} finished. Status: {scraper_run.status}")

    except Exception as e:
        logger.error(f"Scraper run {run_id} crashed: {e}")
        if scraper_run:
            scraper_run.status = "failed"
            scraper_run.end_time = datetime.now()
            db.commit()
    finally:
        db.close()
