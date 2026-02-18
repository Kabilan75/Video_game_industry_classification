import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from app.models import JobListing, KeywordOccurrence

load_dotenv()

def clear_data():
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Clearing GamesIndustry.biz data...")
    
    # Find jobs to delete
    jobs = session.query(JobListing).filter(JobListing.source_website == 'gamesindustry.biz').all()
    print(f"Found {len(jobs)} jobs to delete.")
    
    for job in jobs:
        # Delete occurrences first
        session.query(KeywordOccurrence).filter(KeywordOccurrence.job_id == job.id).delete()
        session.delete(job)
        
    session.commit()
    print("Data cleared.")
    session.close()

if __name__ == "__main__":
    clear_data()
