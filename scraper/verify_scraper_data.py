from sqlalchemy import create_engine, text
import sys
import os

# Point to the database created by the scraper in this directory
db_path = "sqlite:///./games_industry_jobs.db"

if not os.path.exists("./games_industry_jobs.db"):
    print("Database file not found in scraper directory.")
    sys.exit(1)

try:
    engine = create_engine(db_path)
    with engine.connect() as conn:
        print("--- Job Counts by source website ---")
        result = conn.execute(text("SELECT source_website, COUNT(*) FROM job_listings GROUP BY source_website"))
        rows = list(result)
        if not rows:
             print("No jobs found in database.")
        else:
             for row in rows:
                 print(f"{row[0]}: {row[1]}")
        
        print("\n--- Recent Jobs Sample ---")
        recent = conn.execute(text("SELECT source_website, title, company, posting_date FROM job_listings ORDER BY id DESC LIMIT 5"))
        for row in recent:
            print(f"[{row[0]}] {row[1]} at {row[2]} ({row[3]})")
            
except Exception as e:
    print(f"Error: {e}")
