# Deployment Guide

Follow these steps to deploy the Games Industry Job Market Dashboard to a cloud server (AWS, DigitalOcean, Azure, etc.).

## Prerequisites
- A server running Linux (Ubuntu recommended).
- [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
- Git installed.

## 1. Setup on Server

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Kabilan75/Video_game_industry_classification.git
   cd Video_game_industry_classification
   ```

2. **Configure Environment**
   create a production environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if you want to change secrets (optional for simple deployment):
   ```bash
   nano .env
   # Set SECRET_KEY to a random string
   ```

## 2. Deploy

Run the application in **Production Mode**:

```bash
docker-compose --profile production up --build -d
```

- `--profile production`: Enables Nginx and optimized frontend serving.
- `--build`: Rebuilds images to ensure latest code.
- `-d`: Runs in detached mode (background).

**Access the App:**
Open your browser and navigate to your server's IP address or domain (Port 80).

## 3. Initial Data Population

The database starts empty. To populate it with job listings immediately:

```bash
# Enter the backend container
docker exec -it games_industry_backend bash

# Run the manual scraper script
python run_scrapers_manual.py

# Exit container
exit
```

## 4. Maintenance

### Updating Code
To deploy new changes from GitHub:
```bash
git pull origin main
docker-compose --profile production up --build -d
```

### Viewing Logs
```bash
docker-compose logs -f backend
```

### Backup Database
The database is stored in `backend/games_industry_jobs.db`. To backup:
```bash
cp backend/games_industry_jobs.db backup_jobs.db
```
(This file persists across container restarts because of volume mapping).
