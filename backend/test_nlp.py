from app.nlp.keyword_extractor import KeywordExtractor

def test_extraction():
    print("Initializing KeywordExtractor...")
    try:
        extractor = KeywordExtractor()
        print("✓ Extractor initialized")
    except Exception as e:
        print(f"✗ Failed to initialize extractor: {e}")
        return

    sample_text = """
    We are looking for a Senior Game Developer with 5+ years of experience.
    You must be proficient in C++ and Python.
    Experience with Unity or Unreal Engine is required.
    Knowledge of Agile methodologies and Git is a plus.
    """
    
    print("\nExtracting from sample text:")
    print("-" * 40)
    print(sample_text.strip())
    print("-" * 40)
    
    keywords = extractor.extract(sample_text)
    
    print("\nFound keywords:")
    for category, items in keywords.items():
        print(f"  {category.upper()}: {', '.join(items)}")
        
    # Validation
    expected = {
        'skills': ['C++', 'Python', 'Agile', 'Git'], 
        'software': ['Unity', 'Unreal Engine'],
        'experience': ['Senior', '5+ years']
    }
    
    print("\nValidation:")
    all_passed = True
    for cat, items in expected.items():
        found = keywords.get(cat, [])
        # Simple containment check
        for item in items:
            if any(k.lower() == item.lower() for k in found):
                print(f"  ✓ Found {item}")
            else:
                print(f"  ✗ Missing {item}")
                all_passed = False
                
    if all_passed:
        print("\n✅ Extraction test passed!")
    else:
        print("\n⚠️ Extraction issues found.")

if __name__ == "__main__":
    test_extraction()
