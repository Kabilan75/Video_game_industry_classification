# Games Industry Dashboard - Setup Guide

## Initial Setup Steps

### 1. Database Setup

First, create the PostgreSQL database:

```powershell
# Install PostgreSQL (if not already installed)
# Download from: https://www.postgresql.org/download/windows/

# Create database
psql -U postgres
CREATE DATABASE games_industry_jobs;
\q
```

### 2. Environment Variables

Copy `.env.example` to `.env` and update with your credentials:

```powershell
copy .env.example .env
```

Edit `.env` file with:
- Database password
- SMTP credentials (for email alerts)
- Secret key for API authentication

### 3. Backend Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Start the backend:
```powershell
uvicorn app.main:app --reload
```

### 4. Scraper Setup

```powershell
cd scraper
pip install -r requirements.txt
```

### 5. Initial Data Collection

Before running scrapers, note that:
- Spider selectors in `scraper/games_jobs_scraper/spiders/indeed_spider.py` are **PLACEHOLDERS**
- You need to inspect actual website HTML and update CSS selectors
- Test with small batches first

Run scraper:
```powershell
cd scraper
scrapy crawl indeed_games
```

### 6. Verify Data

Check API:
```powershell
# In browser, go to:
http://localhost:8000/docs

# Test endpoints:
http://localhost:8000/api/jobs
http://localhost:8000/admin/stats
```

## Next Steps

1. **Research Target Job Boards**: Identify which games industry job sites to scrape
2. **Update Spider Селекторы**: Customize scrapers for each website
3. **Load Client Keywords**: Get keywords.yaml from client
4. **Implement NLP Pipeline**: Build keyword extraction module
5. **Build Frontend**: Create React dashboard (Phase 5)
6. **Setup Scheduling**: Configure daily automated scraper runs

## Troubleshooting

**Database Connection Error**:
- Verify PostgreSQL is running
- Check DATABASE_URL in .env

**Scraper Not Finding Jobs**:
- Spider selectors need updating
- Website HTML structure may have changed
- Check scrapy logs in console

**Import Errors**:
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
