
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def verify_data():
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Count Jobs
        result = conn.execute(text("SELECT count(*) FROM job_listings"))
        job_count = result.fetchone()[0]
        print(f"Total Jobs: {job_count}")
        
        # Count Keywords
        result = conn.execute(text("SELECT count(*) FROM keywords"))
        keyword_count = result.fetchone()[0]
        print(f"Total Keywords: {keyword_count}")
        
        # Check recent jobs
        if job_count > 0:
            print("\nRecent Jobs:")
            result = conn.execute(text("SELECT title, company, location, is_active, posting_date FROM job_listings ORDER BY scraped_date DESC LIMIT 5"))
            for row in result:
                print(f"- {row[0]} at {row[1]} ({row[2]}) [Active: {row[3]}, Date: {row[4]}]")

if __name__ == "__main__":
    verify_data()
