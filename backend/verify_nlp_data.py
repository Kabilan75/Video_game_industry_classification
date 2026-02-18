import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from app.models import JobListing, Keyword, KeywordOccurrence

load_dotenv()

def verify_data():
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Verifying NLP Data...")
    print("-" * 30)

    # Check Job Listings Aggregated by Source
    from sqlalchemy import func
    source_counts = session.query(JobListing.source_website, func.count(JobListing.id)).group_by(JobListing.source_website).all()
    print("Job Listings by Source:")
    for source, count in source_counts:
        print(f"  - {source}: {count}")

    # Check Job Listings Details (Limit to 5)
    jobs = session.query(JobListing).order_by(JobListing.id.desc()).limit(5).all()
    print(f"\nRecent Jobs found: {len(jobs)}")
    for job in jobs:
        print(f"  Job: {job.title} at {job.company} ({job.source_website})")
        
        # Check Keywords for this job
        occurrences = session.query(KeywordOccurrence).filter_by(job_id=job.id).all()
        print(f"    Keywords found: {len(occurrences)}")
        
        for occ in occurrences:
            keyword = session.query(Keyword).get(occ.keyword_id)
            print(f"      - {keyword.keyword} ({keyword.category}): {occ.frequency}")

    # Check Total Keywords
    total_keywords = session.query(Keyword).count()
    print(f"\nTotal unique keywords in DB: {total_keywords}")
    
    session.close()

if __name__ == "__main__":
    verify_data()
