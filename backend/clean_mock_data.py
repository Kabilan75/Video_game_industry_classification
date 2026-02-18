import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from app.models import Base, JobListing, KeywordOccurrence

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_mock_data():
    session = SessionLocal()
    try:
        # Find mock jobs
        mock_jobs = session.query(JobListing).filter(JobListing.source_website == 'mock_source').all()
        
        if not mock_jobs:
            print("No mock data found.")
            return

        print(f"Found {len(mock_jobs)} mock jobs. Deleting...")
        
        for job in mock_jobs:
            # Delete associated keyword occurrences first (though cascade might handle it, being safe)
            session.query(KeywordOccurrence).filter(KeywordOccurrence.job_id == job.id).delete()
            session.delete(job)
            print(f"Deleted: {job.title}")

        session.commit()
        print("Mock data cleared successfully.")
        
    except Exception as e:
        print(f"Error clearing data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clean_mock_data()
