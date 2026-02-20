# Deploying to Render.com

This guide explains how to deploy the Games Industry Job Market Dashboard to [Render](https://render.com) for free.
We use a **Single Container** approach (Frontend + Backend combined) to stay within the free tier easily.

## 1. Prerequisites
- A GitHub account.
- A Render.com account.
- Your code pushed to GitHub (see below).

## 2. Prepare Repository

Run these commands locally to push the latest changes (including the new `Dockerfile.render`):

```bash
git add .
git commit -m "feat: add render deployment config"
git push origin main
```

## 3. Create Web Service on Render

1.  Log in to [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  Give it a name (e.g., `games-jobs-dashboard`).
5.  **Runtime**: Select **Docker**.
6.  **Region**: Choose closest to you (e.g., Oregon, Frankfurt).
7.  **Branch**: `main`.

### Important Configuration
Scroll down to the Advanced section or Environment variables:

- **Dockerfile Path**: `Dockerfile.render`  
  *(Crucial! Do not use the default `Dockerfile`, as `Dockerfile.render` combines backend+frontend).*

- **Persistent Disk** (Recommended for SQLite):
    - Click **Advanced** -> **Add Disk**.
    - Name: `sqlite-data`
    - Mount Path: `/data`
    - Size: `1 GB`

- **Environment Variables**:
    - `DATABASE_URL`: `sqlite:////data/games_industry_jobs.db`
    - `PORT`: `10000`
    - `LOG_LEVEL`: `INFO`
    - `SECRET_KEY`: (Generate a random string)

8.  Click **Create Web Service**.

## 4. Verification

Render will start building your unified Docker image. This may take 3-5 minutes.
Once done, it will deploy and give you a URL (e.g., `https://games-jobs-dashboard.onrender.com`).

- **Frontend**: Accessible at the root URL.
- **Backend API**: Accessible at `/api/...` allowed.
- **Scrapers**: The scheduler runs automatically in the background.

## 5. Persistence Note
Because we mounted a disk at `/data`, your `games_industry_jobs.db` will be safe even if the web service restarts or deploys new code.
