"""
Clear all job data from the database so we can re-scrape London-only jobs.
Uses DELETE in dependency order to avoid FK constraint issues.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Deleting all job-related data...")

    # Delete in FK-safe order (children first)
    r1 = conn.execute(text("DELETE FROM keyword_occurrences;"))
    print(f"  keyword_occurrences deleted: {r1.rowcount}")

    r2 = conn.execute(text("DELETE FROM keywords;"))
    print(f"  keywords deleted: {r2.rowcount}")

    r3 = conn.execute(text("DELETE FROM regional_summaries;"))
    print(f"  regional_summaries deleted: {r3.rowcount}")

    r4 = conn.execute(text("DELETE FROM scraper_runs;"))
    print(f"  scraper_runs deleted: {r4.rowcount}")

    r5 = conn.execute(text("DELETE FROM job_listings;"))
    print(f"  job_listings deleted: {r5.rowcount}")

    conn.commit()
    print("\n✅ Database cleared successfully.")

    # Verify
    result = conn.execute(text("SELECT COUNT(*) FROM job_listings;"))
    count = result.scalar()
    print(f"   job_listings remaining: {count}")
