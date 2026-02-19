from datetime import datetime
from app.services.scraper_service import run_all_uk_spiders
from app.database import SessionLocal
from app.models import ScraperRun
import logging

# Configure basic logging to focus on the run
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manual_run")

def main():
    print("🚀 Initializing Manual Scraper Run...")
    
    # 1. Create a ScraperRun record
    db = SessionLocal()
    try:
        run = ScraperRun(
            start_time=datetime.now(),
            status="pending",
            source_website="all_uk_manual_run",
            jobs_scraped=0,
            duplicates_found=0,
            errors_count=0
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id
        print(f"✅ Created ScraperRun ID: {run_id}")
    except Exception as e:
        print(f"❌ Failed to create run record: {e}")
        db.close()
        return

    db.close()

    # 2. Run the spiders
    print(f"🕷️  Starting spiders for run {run_id}...")
    try:
        run_all_uk_spiders(run_id)
        print("✅ Run completed. Check dashboard or logs for details.")
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    main()
