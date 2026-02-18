"""
Database models for the Games Industry Jobs Dashboard.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Index, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class JobListing(Base):
    """Job listing model."""
    
    __tablename__ = "job_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    location = Column(String, index=True)
    description = Column(Text)
    salary = Column(String, nullable=True)
    posting_date = Column(DateTime, index=True)
    scraped_date = Column(DateTime, default=func.now(), index=True)
    source_website = Column(String, index=True)
    content_hash = Column(String(64), index=True)  # For duplicate detection
    is_active = Column(Integer, default=1)  # 1 = active, 0 = removed/expired
    
    # Relationships
    keyword_occurrences = relationship("KeywordOccurrence", back_populates="job")
    
    # Composite unique constraint for duplicate prevention
    __table_args__ = (
        UniqueConstraint('url', 'company', 'title', name='uq_job_listing'),
        Index('idx_posting_date', 'posting_date'),
        Index('idx_location_date', 'location', 'posting_date'),
        Index('idx_company_date', 'company', 'posting_date'),
    )
    
    def __repr__(self):
        return f"<JobListing(id={self.id}, title='{self.title}', company='{self.company}')>"


class Keyword(Base):
    """Keyword model for skills, software, and experience tracking."""
    
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=False, index=True)  # skill, software, experience
    client_provided = Column(Integer, default=1)  # 1 = from client list, 0 = auto-discovered
    
    # Relationships
    occurrences = relationship("KeywordOccurrence", back_populates="keyword")
    
    __table_args__ = (
        Index('idx_category', 'category'),
    )
    
    def __repr__(self):
        return f"<Keyword(id={self.id}, keyword='{self.keyword}', category='{self.category}')>"


class KeywordOccurrence(Base):
    """Tracks keyword occurrences in job listings."""
    
    __tablename__ = "keyword_occurrences"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_listings.id"), nullable=False, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, index=True)
    frequency = Column(Integer, default=1)  # Number of times keyword appears in job
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    job = relationship("JobListing", back_populates="keyword_occurrences")
    keyword = relationship("Keyword", back_populates="occurrences")
    
    __table_args__ = (
        UniqueConstraint('job_id', 'keyword_id', name='uq_job_keyword'),
        Index('idx_job_keyword', 'job_id', 'keyword_id'),
    )
    
    def __repr__(self):
        return f"<KeywordOccurrence(job_id={self.job_id}, keyword_id={self.keyword_id}, frequency={self.frequency})>"


class RegionalSummary(Base):
    """Pre-aggregated regional data for faster dashboard queries."""
    
    __tablename__ = "regional_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, index=True)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    keyword = relationship("Keyword")
    
    __table_args__ = (
        UniqueConstraint('region', 'date', 'keyword_id', name='uq_regional_summary'),
        Index('idx_region_date', 'region', 'date'),
    )
    
    def __repr__(self):
        return f"<RegionalSummary(region='{self.region}', date={self.date}, count={self.count})>"


class ScraperRun(Base):
    """Tracks scraper execution history."""
    
    __tablename__ = "scraper_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    source_website = Column(String, nullable=False)
    jobs_scraped = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    status = Column(String, default="running")  # running, completed, failed
    
    __table_args__ = (
        Index('idx_start_time', 'start_time'),
        Index('idx_source_status', 'source_website', 'status'),
    )
    
    def __repr__(self):
        return f"<ScraperRun(id={self.id}, source='{self.source_website}', status='{self.status}')>"
