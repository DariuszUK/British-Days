#!/usr/bin/env python3
"""
Test script for British Days application (headless mode).
Tests database and search functionality without GUI.
"""
import os
import sys

print("=" * 60)
print("British Days Application - Test Suite")
print("=" * 60)

# Test 1: Database Module
print("\n1. Testing Database Module...")
try:
    from database import DatabaseManager
    
    db = DatabaseManager()
    print(f"   ✓ Database initialized")
    print(f"   ✓ Location: {db.db_path}")
    
    # Add test terms
    success, tid = db.add_term("test_term", "Test definition", "Test example", "test")
    if success:
        print(f"   ✓ Added test term (ID: {tid})")
    
    # Get stats
    stats = db.get_database_stats()
    print(f"   ✓ Database stats: {stats['total_terms']} terms")
    
    # Clean up - delete the db object
    del db
    
    print("   ✓ Database module: PASSED")
except Exception as e:
    print(f"   ✗ Database module: FAILED - {e}")
    sys.exit(1)

# Test 2: Search Module
print("\n2. Testing Search Module...")
try:
    from search import SlangSearcher
    
    searcher = SlangSearcher()
    print(f"   ✓ Searcher initialized")
    
    # Perform search
    result = searcher.search_new_slang()
    print(f"   ✓ Search returned: {result['term']}")
    print(f"   ✓ Definition: {result['definition'][:50]}...")
    
    print("   ✓ Search module: PASSED")
except Exception as e:
    print(f"   ✗ Search module: FAILED - {e}")
    sys.exit(1)

# Test 3: Integration Test
print("\n3. Testing Integration (Search + Database)...")
try:
    # Recreate database manager for this test
    db = DatabaseManager()
    
    # Search for 5 new terms and add to database
    added_count = 0
    duplicate_count = 0
    
    for i in range(5):
        result = searcher.search_new_slang()
        success, tid = db.add_term(
            result['term'],
            result['definition'],
            result.get('example', ''),
            result.get('category', 'slang'),
            'test'
        )
        if success:
            added_count += 1
        else:
            duplicate_count += 1
    
    print(f"   ✓ Added {added_count} new terms")
    print(f"   ✓ Skipped {duplicate_count} duplicates")
    
    # Verify database
    stats = db.get_database_stats()
    print(f"   ✓ Total terms in database: {stats['total_terms']}")
    
    # Display some terms
    terms = db.get_all_terms()
    print(f"\n   Sample terms from database:")
    for i, term in enumerate(terms[:3], 1):
        term_id, term_name, definition, example, category, date_added, source, polish, pronunciation = term
        print(f"   {i}. {term_name}: {definition[:40]}...")
    
    print("\n   ✓ Integration test: PASSED")
except Exception as e:
    print(f"   ✗ Integration test: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Configuration
print("\n4. Testing Configuration...")
try:
    import json
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print(f"   ✓ Config loaded")
    print(f"   ✓ Window title: {config['window_title']}")
    print(f"   ✓ Data directory: {config['data_directory']}")
    print(f"   ✓ Configuration: PASSED")
except Exception as e:
    print(f"   ✗ Configuration: FAILED - {e}")
    sys.exit(1)

# Test 5: Assets
print("\n5. Testing PNG Assets...")
try:
    assets_dir = 'assets'
    required_assets = [
        'background.png',
        'btn_search.png',
        'btn_refresh.png',
        'btn_exit.png',
        'panel_main.png',
        'logo.png'
    ]
    
    missing = []
    for asset in required_assets:
        path = os.path.join(assets_dir, asset)
        if not os.path.exists(path):
            missing.append(asset)
    
    if missing:
        print(f"   ✗ Missing assets: {', '.join(missing)}")
        sys.exit(1)
    
    print(f"   ✓ All {len(required_assets)} PNG assets found")
    print(f"   ✓ Assets: PASSED")
except Exception as e:
    print(f"   ✗ Assets: FAILED - {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
print("\nApplication is ready to run!")
print("Note: GUI requires a display server to test interactively.")
print("\nTo run the application:")
print("  python main.py")
print("\nTo build Windows executable:")
print("  python build.py")
print("=" * 60)
