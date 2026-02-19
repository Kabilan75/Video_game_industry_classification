# Maintenance Guide — UK Games Industry Dashboard

> **Audience**: Developers or administrators responsible for day-to-day operation.

---

## Daily Operations

### Automatic Tasks (No Action Required)
| Time | Task | Description |
|------|------|-------------|
| 03:00 AM | Daily scrape | All 6 Scrapy spiders run sequentially |
| 04:00 AM | Regional summary refresh | `RegionalSummary` table rebuilt from current data |

### Manual Triggers
You can trigger these via the Admin API or directly in a terminal.

**Manually run a scrape:**
```bash
# Via API (POST)
curl -X POST http://localhost:8000/admin/scrape

# Or directly via Scrapy (from the scraper/ folder)
cd scraper
python -m scrapy crawl gamesindustry_uk
```

**Refresh regional summary:**
```bash
# The scheduler does this automatically, but to trigger now:
# Start the backend and call:
curl http://localhost:8000/admin/stats
```

---

## Data Quality Monitoring

Check the data quality report at any time:
```
GET http://localhost:8000/admin/data-quality
```

This returns:
- Total active jobs
- Jobs missing location / description (with %)
- Jobs with no keywords extracted
- List of raw location string variants

**Action items if quality drops:**
1. Open `config/keywords.yaml` and add new terms that the NLP misses
2. Update the location mapping in `scraper/games_jobs_scraper/pipelines.py` → `DataCleaningPipeline.location_mapping`

---

## Adding New Keywords

1. Open `config/keywords.yaml`
2. Add your keyword under the correct category (`skills`, `software`, `experience`)
3. Restart the backend (new keywords are loaded on startup via `KeywordExtractor`)
4. Run a scrape to backfill existing jobs: `POST /admin/scrape`

---

## Adding New Spider / Job Source

1. Create a new spider file in `scraper/games_jobs_scraper/spiders/`
2. Inherit from `scrapy.Spider` and yield items with fields: `url`, `title`, `company`, `location`, `description`, `source_website`, `posting_date`
3. Add the spider name to `run_all_uk_spiders()` in `backend/app/services/scraper_service.py`

---

## Exporting Data

| Export | URL |
|--------|-----|
| All jobs (CSV) | `GET /api/export/jobs` |
| Jobs filtered | `GET /api/export/jobs?location=London&keyword=Unity` |
| Keywords (CSV) | `GET /api/export/keywords` |
| Regional (CSV) | `GET /api/export/regional` |

Available from the dashboard via the **Export CSV** buttons on Jobs, Trends, and Regional pages.

---

## Viewing Scraper Logs

```bash
# Backend logs
cat backend/backend.log

# Scraper run history via API
curl http://localhost:8000/admin/scraper-status
```

---

## Restarting Services

```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev

# Full stack (Docker)
docker-compose up --build
```

---

## Database

- **Dev**: `backend/games_industry_jobs.db` (SQLite)
- **Prod**: PostgreSQL (configure `DATABASE_URL` in `.env`)

To clear all data and start fresh:
```bash
python backend/clear_database.py
```

---

## Common Issues

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| No jobs showing | Scraper not run | `POST /admin/scrape` |
| Trends chart empty | Date range too narrow | Widen to 90+ days |
| Regional data missing | `RegionalSummary` not populated | Trigger scrape or wait for 4AM job |
| Keywords not extracted | spaCy model missing | `python -m spacy download en_core_web_sm` |
| CSV download fails | Backend not running | Check backend is up on port 8000 |
