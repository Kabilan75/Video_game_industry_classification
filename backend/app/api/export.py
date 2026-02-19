"""
Export API endpoints.
Provides CSV download for jobs and keyword data.
"""

import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import JobListing, Keyword, KeywordOccurrence
from logging_config import get_logger

router = APIRouter()
logger = get_logger("api")


@router.get("/jobs")
async def export_jobs_csv(
    db: Session = Depends(get_db),
    location: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """
    Export filtered job listings as a CSV file download.
    """
    query = db.query(JobListing).filter(JobListing.is_active != 0)

    if location:
        query = query.filter(JobListing.location.ilike(f"%{location}%"))
    if company:
        query = query.filter(JobListing.company.ilike(f"%{company}%"))
    if keyword:
        query = query.filter(
            (JobListing.title.ilike(f"%{keyword}%")) |
            (JobListing.description.ilike(f"%{keyword}%"))
        )
    if start_date:
        query = query.filter(JobListing.posting_date >= start_date)
    if end_date:
        query = query.filter(JobListing.posting_date <= end_date)

    jobs = query.order_by(JobListing.posting_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Company", "Location", "Salary", "Posting Date", "Source", "URL"])
    for j in jobs:
        writer.writerow([
            j.id,
            j.title,
            j.company,
            j.location or "",
            j.salary or "",
            j.posting_date.strftime("%Y-%m-%d") if j.posting_date else "",
            j.source_website or "",
            j.url,
        ])

    output.seek(0)
    filename = f"games_industry_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
    logger.info(f"Exporting {len(jobs)} jobs to CSV")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/keywords")
async def export_keywords_csv(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None),
):
    """
    Export keyword frequency data as a CSV file download.
    """
    query = (
        db.query(
            Keyword.keyword,
            Keyword.category,
            func.sum(KeywordOccurrence.frequency).label("total_frequency"),
            func.count(KeywordOccurrence.job_id.distinct()).label("job_count")
        )
        .join(KeywordOccurrence)
        .join(JobListing)
    )
    if category:
        query = query.filter(Keyword.category == category)

    results = (
        query
        .group_by(Keyword.id, Keyword.keyword, Keyword.category)
        .order_by(desc("total_frequency"))
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Keyword", "Category", "Total Mentions", "Jobs Containing"])
    for r in results:
        writer.writerow([r.keyword, r.category, r.total_frequency, r.job_count])

    output.seek(0)
    filename = f"games_industry_keywords_{datetime.now().strftime('%Y%m%d')}.csv"
    logger.info(f"Exporting {len(results)} keywords to CSV")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/regional")
async def export_regional_csv(db: Session = Depends(get_db)):
    """
    Export regional job distribution as CSV.
    """
    results = (
        db.query(
            JobListing.location,
            func.count(JobListing.id).label("job_count")
        )
        .filter(JobListing.is_active != 0)
        .group_by(JobListing.location)
        .order_by(func.count(JobListing.id).desc())
        .all()
    )

    total = sum(r.job_count for r in results)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Region", "Job Count", "Share (%)"])
    for r in results:
        pct = round((r.job_count / total) * 100, 2) if total > 0 else 0
        writer.writerow([r.location or "Unknown", r.job_count, pct])

    output.seek(0)
    filename = f"games_industry_regional_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
