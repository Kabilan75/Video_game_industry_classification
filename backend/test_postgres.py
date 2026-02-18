"""
Test script to verify PostgreSQL connection and backend setup.
Run this after PostgreSQL is installed and database is created.
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def test_postgres_connection():
    """Test PostgreSQL connection."""
    print("Testing PostgreSQL connection...")
    
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("[FAIL] DATABASE_URL not found in .env file")
            return False
        
        print(f"Connecting to: {database_url.replace(database_url.split(':')[2].split('@')[0], '***')}")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"[PASS] Connected to PostgreSQL successfully!")
            print(f"  Version: {version[:50]}...")
            
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure PostgreSQL is installed and running")
        print("  2. Verify the database 'games_industry_jobs' exists")
        print("  3. Check username/password in .env file")
        print("  4. Ensure PostgreSQL is listening on port 5433")
        return False


def test_database_creation():
    """Test that tables can be created."""
    print("\nTesting database table creation...")
    
    try:
        from app.database import engine, init_db
        
        print("Creating tables...")
        init_db()
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['job_listings', 'keywords', 'keyword_occurrences', 'regional_summary', 'scraper_runs']
        
        print(f"[PASS] Database tables created successfully!")
        print(f"  Found {len(tables)} tables:")
        for table in tables:
            status = "[PASS]" if table in expected_tables else "[?]"
            print(f"    {status} {table}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Table creation failed: {e}")
        return False


def test_api_startup():
    """Test that FastAPI app can start."""
    print("\nTesting FastAPI app...")
    
    try:
        from app.main import app
        
        print(f"[PASS] FastAPI app loaded successfully")
        print(f"  - Routes: {len(app.routes)}")
        print(f"  - Title: {app.title}")
        
        # List key endpoints
        print("  - Key endpoints:")
        for route in app.routes:
            if hasattr(route, 'path') and route.path.startswith('/api'):
                print(f"    - {route.path}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] FastAPI app failed: {e}")
        return False


def log(message, file):
    """Print to console and file."""
    print(message)
    file.write(message + "\n")

def main():
    """Run all tests."""
    with open("test_results.log", "w") as f:
        log("="* 60, f)
        log("POSTGRESQL + BACKEND VERIFICATION", f)
        log("="* 60, f)
        
        results = []
        
        # Test 1: PostgreSQL connection
        results.append(("PostgreSQL Connection", test_postgres_connection()))
        
        # Test 2: Database table creation (only if connection works)
        if results[0][1]:
            results.append(("Database Tables", test_database_creation()))
        
        # Test 3: FastAPI app
        results.append(("FastAPI App", test_api_startup()))
        
        log("\n" + "="* 60, f)
        log("TEST SUMMARY", f)
        log("="* 60, f)
        
        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            log(f"{status}: {name}", f)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        log(f"\nPassed: {passed}/{total}", f)
        
        if passed == total:
            log("\nAll tests passed!", f)
            log("\nNext step: Start the backend server", f)
            log("  Command: uvicorn app.main:app --reload", f)
            log("  Then visit: http://localhost:8000/docs", f)
        else:
            log(f"\nWarning: {total - passed} test(s) failed.", f)
            log("Please fix issues before proceeding.", f)


if __name__ == "__main__":
    main()
