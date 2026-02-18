# PostgreSQL Setup Instructions

## After Installing PostgreSQL

### 1. Create the Database

Open PostgreSQL command prompt (SQL Shell - psql) or use pgAdmin:

```sql
-- Connect as postgres user
-- Password: (whatever you set during installation)

-- Create the database
CREATE DATABASE games_industry_jobs;

-- Verify it was created
\l
```

Or using command line:
```powershell
# Using psql command
psql -U postgres
# Enter password when prompted

CREATE DATABASE games_industry_jobs;
\q
```

### 2. Update .env File

Edit `.env` and update the password if you set a different one during installation:

```bash
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/games_industry_jobs
```

Replace `YOUR_PASSWORD` with the password you set for the postgres user during installation.

### 3. Start the Backend

```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

The backend will automatically:
- Connect to PostgreSQL
- Create all tables with indexes
- Start the API on http://localhost:8000

### 4. Verify Setup

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Stats**: http://localhost:8000/admin/stats

### 5. Test Endpoints

In the API docs (http://localhost:8000/docs):
1. Try `GET /health` - Should return `{"status": "healthy"}`
2. Try `GET /admin/stats` - Should return database statistics (all zeros for now)
3. Try `GET /api/jobs` - Should return empty list (no jobs scraped yet)

## Troubleshooting

**Connection Error**:
- Make sure PostgreSQL service is running
- Check Windows Services for "postgresql-x64-XX" service
- Verify password in `.env` matches your PostgreSQL password

**Port Already in Use**:
- PostgreSQL default port is 5432
- Check if it's running: `netstat -ano | findstr :5432`

**Permission Denied**:
- Make sure you're using the correct postgres user password
- Try connecting with pgAdmin to verify credentials

## Next Steps After Setup

Once the backend is running successfully:
1. We'll test the API endpoints
2. Then implement the NLP keyword extraction (Phase 3)
3. Finally build the frontend dashboard (Phase 5)
