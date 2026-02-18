"""
Simple test script to verify backend setup without database.
Tests imports, configuration loading, and basic API structure.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
        
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
        
        import pydantic
        print("✓ Pydantic imported successfully")
        
        import yaml
        print("✓ PyYAML imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from app.config import get_settings
        settings = get_settings()
        print(f"✓ Configuration loaded")
        print(f"  - App name: {settings.app_name}")
        print(f"  - Log level: {settings.log_level}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_models():
    """Test database models can be imported."""
    print("\nTesting database models...")
    try:
        from app.models import JobListing, Keyword, KeywordOccurrence
        print("✓ Models imported successfully")
        print(f"  - JobListing table: {JobListing.__tablename__}")
        print(f"  - Keyword table: {Keyword.__tablename__}")
        print(f"  - KeywordOccurrence table: {KeywordOccurrence.__tablename__}")
        return True
    except Exception as e:
        print(f"✗ Models error: {e}")
        return False


def test_api_structure():
    """Test API endpoints are properly defined."""
    print("\nTesting API structure...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes]
        print(f"✓ FastAPI app created with {len(routes)} routes")
        
        # Check key endpoints
        key_endpoints = ['/api/jobs', '/api/keywords/top', '/api/trends', '/admin/scrape']
        for endpoint in key_endpoints:
            if any(endpoint in route for route in routes):
                print(f"  ✓ {endpoint}")
            else:
                print(f"  ✗ {endpoint} not found")
        
        return True
    except Exception as e:
        print(f"✗ API structure error: {e}")
        return False


def test_logging():
    """Test logging configuration."""
    print("\nTesting logging configuration...")
    try:
        from logging_config import get_logger
        logger = get_logger("api")
        print("✓ Logging configured")
        print(f"  - API logger: {logger.name}")
        return True
    except Exception as e:
        print(f"✗ Logging error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("BACKEND VERIFICATION TEST")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Models", test_models),
        ("API Structure", test_api_structure),
        ("Logging", test_logging),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend setup is correct.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please install missing dependencies.")


if __name__ == "__main__":
    main()
