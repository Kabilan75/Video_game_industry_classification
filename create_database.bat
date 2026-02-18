@echo off
REM Create PostgreSQL database for Games Industry Dashboard
REM Run this batch file to create the database

set PGPASSWORD=Kabilan@123
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5433 -c "CREATE DATABASE games_industry_jobs;"

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Database 'games_industry_jobs' created successfully!
) else (
    echo ERROR: Failed to create database. It may already exist or there may be a connection issue.
)

pause
