"""
Scrapy pipelines for processing scraped items.
Handles data cleaning, duplicate detection, and database storage.
"""

import hashlib
import re
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
import os
from dotenv import load_dotenv
import Levenshtein

load_dotenv()


class DataCleaningPipeline:
    """Clean and standardize scraped data."""
    
    def process_item(self, item, spider):
        # Clean and standardize location
        if item.get('location'):
            location = item['location']
            # Remove extra whitespace
            location = ' '.join(location.split())
            # Standardize common UK location variations
            location_mapping = {
                'leicester': 'Leicester',
                'leicestershire': 'Leicester',
                'london': 'London',
                'greater london': 'London',
                'nottingham': 'Nottingham',
                'nottinghamshire': 'Nottingham',
                'leamington spa': 'Leamington Spa',
                'leamington': 'Leamington Spa',
                'birmingham': 'Birmingham',
                'manchester': 'Manchester',
                'liverpool': 'Liverpool',
                'glasgow': 'Glasgow',
                'edinburgh': 'Edinburgh',
                'bristol': 'Bristol',
                'cambridge': 'Cambridge',
                'oxford': 'Oxford',
            }
            
            location_lower = location.lower()
            for key, value in location_mapping.items():
                if key in location_lower:
                    location = value
                    break
            
            item['location'] = location
        
        # Clean title
        if item.get('title'):
            item['title'] = ' '.join(item['title'].split())
        
        # Clean company name
        if item.get('company'):
            item['company'] = ' '.join(item['company'].split())
        
        # Generate content hash for duplicate detection
        content = f"{item.get('title', '')}{item.get('company', '')}{item.get('location', '')}{item.get('description', '')[:200]}"
        item['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
        
        # Set scraped date
        item['scraped_date'] = datetime.now()
        
        return item


class DuplicateDetectionPipeline:
    """Detect and handle duplicate job listings."""
    
    def __init__(self):
        self.seen_hashes = set()
        self.seen_urls = set()
    
    def process_item(self, item, spider):
        # Check URL-based duplicates
        if item['url'] in self.seen_urls:
            spider.logger.info(f"Duplicate URL found: {item['url']}")
            raise DropItem(f"Duplicate URL: {item['url']}")
        
        # Check hash-based duplicates
        if item['content_hash'] in self.seen_hashes:
            spider.logger.info(f"Duplicate content found: {item['title']} at {item['company']}")
            raise DropItem(f"Duplicate content: {item['title']}")
        
        self.seen_urls.add(item['url'])
        self.seen_hashes.add(item['content_hash'])
        
        return item


class DatabasePipeline:
    """Store scraped items in PostgreSQL database."""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.extractor = None
    
    def open_spider(self, spider):
        """Initialize database connection and keyword extractor."""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            spider.logger.error("DATABASE_URL not found in environment variables")
            return
        
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize Keyword Extractor
        try:
            # Add backend path to sys.path to import extractor
            import sys
            backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
            spider.logger.info(f"Calculated backend path: {backend_path}")
            
            if backend_path not in sys.path:
                sys.path.append(backend_path)
            
            # Verify we can find the path
            if not os.path.exists(backend_path):
                 spider.logger.error(f"Backend path does not exist: {backend_path}")
            else:
                 spider.logger.info(f"Backend path exists. Contents: {os.listdir(backend_path)}")

            from app.nlp.keyword_extractor import KeywordExtractor
            # Path to keywords.yaml relative to scraper
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config/keywords.yaml'))
            self.extractor = KeywordExtractor(config_path)
            spider.logger.info(f"Keyword Extractor initialized with config: {config_path}")
        except Exception as e:
            spider.logger.error(f"Failed to initialize Keyword Extractor: {e}")
        
        spider.logger.info("Database connection established")
    
    def close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.engine:
            self.engine.dispose()
            spider.logger.info("Database connection closed")
    
    def process_item(self, item, spider):
        """Save item to database."""
        if not self.Session:
            spider.logger.warning("Database session not initialized, skipping item")
            return item
        
        session = self.Session()
        
        try:
            # Import models here to avoid circular imports
            # Ensure backend is in path (should be from open_spider)
            from app.models import JobListing, Keyword, KeywordOccurrence
            
            # 1. Save Job Listing
            existing_job = session.query(JobListing).filter(
                (JobListing.url == item['url']) |
                (JobListing.content_hash == item['content_hash'])
            ).first()
            
            job = None
            if existing_job:
                # Update scraped_date to mark as still active
                existing_job.scraped_date = item['scraped_date']
                spider.logger.info(f"Updated existing job: {item['title']}")
                job = existing_job
            else:
                # Create new job listing
                job = JobListing(
                    url=item['url'],
                    title=item['title'],
                    company=item['company'],
                    location=item.get('location'),
                    description=item.get('description'),
                    salary=item.get('salary'),
                    posting_date=item.get('posting_date'),
                    source_website=item['source_website'],
                    scraped_date=item['scraped_date'],
                    content_hash=item['content_hash'],
                    is_active=1
                )
                session.add(job)
                session.flush()  # Get ID without committing yet
                spider.logger.info(f"Added new job: {item['title']}")
            
            # 2. Extract and Save Keywords (only if we have an extractor and description)
            if self.extractor and item.get('description'):
                # Extract keywords
                extracted_data = self.extractor.extract_with_counts(item['description'])
                
                # Flatten detected keywords
                for category, keywords_dict in extracted_data.items():
                    for keyword_text, count in keywords_dict.items():
                        # Find or create keyword
                        keyword_obj = session.query(Keyword).filter(
                            func.lower(Keyword.keyword) == keyword_text.lower()
                        ).first()
                        
                        if not keyword_obj:
                            keyword_obj = Keyword(
                                keyword=keyword_text,
                                category=category,
                                client_provided=1 # Assuming all matches are from our client list
                            )
                            session.add(keyword_obj)
                            session.flush()
                        
                        # Check if occurrence exists
                        occurrence = session.query(KeywordOccurrence).filter_by(
                            job_id=job.id,
                            keyword_id=keyword_obj.id
                        ).first()
                        
                        if occurrence:
                            occurrence.frequency = count
                        else:
                            occurrence = KeywordOccurrence(
                                job_id=job.id,
                                keyword_id=keyword_obj.id,
                                frequency=count
                            )
                            session.add(occurrence)
                
                # Store extracted keywords in item for debugging
                item['keywords'] = extracted_data

            session.commit()
            
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error saving to database: {str(e)}")
            # Don't raise here to allow pipeline to continue, but log error
            # raise
        
        finally:
            session.close()
        
        return item


from scrapy.exceptions import DropItem
