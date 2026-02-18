"""Quick verification test - run without database."""
print("Testing backend imports...")

try:
    from app import models, config, schemas
    print("✓ App modules imported")
    
    from app.config import get_settings
    settings = get_settings()
    print(f"✓ Config loaded: {settings.app_name}")
    
    from app.models import JobListing, Keyword
    print(f"✓ Models loaded: {JobListing.__tablename__}, {Keyword.__tablename__}")
    
    print("\n✅ Backend structure is valid!")
    print("\nNote: To fully test, you need:")
    print("  1. PostgreSQL running (or Docker)")
    print("  2. Run: uvicorn app.main:app --reload")
    print("  3. Visit: http://localhost:8000/docs")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
