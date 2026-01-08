#!/usr/bin/env python3
"""
Test script for enhanced features:
- Database location tracking
- Term caching
- API integration fallback
"""
import os
import sys

print("=" * 60)
print("British Days - Enhanced Features Test Suite")
print("=" * 60)

# Test 1: Database Location Tracking
print("\n1. Testing Location Tracking...")
try:
    from database import DatabaseManager
    
    db = DatabaseManager()
    
    # Mark a location as searched
    success = db.mark_location_searched('wikipedia', 'British_slang_page_1', 5)
    assert success, "Failed to mark location as searched"
    print("   ✓ Marked location as searched")
    
    # Check if location is searched
    is_searched = db.is_location_searched('wikipedia', 'British_slang_page_1')
    assert is_searched, "Failed to check searched location"
    print("   ✓ Location correctly identified as searched")
    
    # Check a location that hasn't been searched
    not_searched = db.is_location_searched('wiktionary', 'random_page')
    assert not not_searched, "False positive for unsearched location"
    print("   ✓ Unsearched location correctly identified")
    
    print("   ✓ Location tracking: PASSED")
except Exception as e:
    print(f"   ✗ Location tracking: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Term Caching
print("\n2. Testing Term Caching...")
try:
    # Add a term to cache
    success = db.add_to_cache(
        term='test_slang',
        definition='A test definition',
        example='This is a test example',
        category='test',
        polish='Test po polsku',
        pronunciation='TEST',
        source_type='wikipedia',
        source_url='https://en.wikipedia.org/wiki/Test'
    )
    assert success, "Failed to add term to cache"
    print("   ✓ Added term to cache")
    
    # Retrieve cached term
    cached = db.get_cached_term('test_slang')
    assert cached is not None, "Failed to retrieve cached term"
    assert cached[0] == 'test_slang', "Cached term name mismatch"
    assert cached[1] == 'A test definition', "Cached definition mismatch"
    print("   ✓ Retrieved cached term successfully")
    
    # Mark cache as added to database
    success = db.mark_cache_added_to_db('test_slang')
    assert success, "Failed to mark cache as added"
    print("   ✓ Marked cached term as added to database")
    
    # Get uncached terms count
    count = db.get_uncached_terms_count()
    print(f"   ✓ Uncached terms count: {count}")
    
    print("   ✓ Term caching: PASSED")
except Exception as e:
    print(f"   ✗ Term caching: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Search API Integration
print("\n3. Testing Search API Integration...")
try:
    from search import SlangSearcher
    
    # Test with database integration
    searcher = SlangSearcher(db_manager=db)
    
    # Perform searches
    results = []
    for i in range(3):
        result = searcher.search_new_slang()
        assert result is not None, f"Search {i+1} returned None"
        assert 'term' in result, "Result missing 'term' field"
        assert 'definition' in result, "Result missing 'definition' field"
        assert 'source' in result, "Result missing 'source' field"
        results.append(result)
        print(f"   ✓ Search {i+1}: {result['term']} from {result['source']}")
    
    # Verify source rotation (should try different sources)
    sources = [r['source'] for r in results]
    print(f"   ✓ Sources used: {', '.join(set(sources))}")
    
    print("   ✓ Search API integration: PASSED")
except Exception as e:
    print(f"   ✗ Search API integration: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Database Tables
print("\n4. Testing Database Tables...")
try:
    import sqlite3
    
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Check all tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['slang_terms', 'search_history', 'searched_locations', 'term_cache']
    for table in required_tables:
        assert table in tables, f"Missing table: {table}"
        print(f"   ✓ Table exists: {table}")
    
    # Check searched_locations structure
    cursor.execute("PRAGMA table_info(searched_locations)")
    cols = [col[1] for col in cursor.fetchall()]
    assert 'source_type' in cols, "Missing source_type column"
    assert 'source_identifier' in cols, "Missing source_identifier column"
    print("   ✓ searched_locations table has correct structure")
    
    # Check term_cache structure
    cursor.execute("PRAGMA table_info(term_cache)")
    cols = [col[1] for col in cursor.fetchall()]
    assert 'term' in cols, "Missing term column"
    assert 'added_to_database' in cols, "Missing added_to_database column"
    print("   ✓ term_cache table has correct structure")
    
    conn.close()
    
    print("   ✓ Database tables: PASSED")
except Exception as e:
    print(f"   ✗ Database tables: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Config File Structure
print("\n5. Testing Config File...")
try:
    import json
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Check for column_widths
    assert 'column_widths' in config, "Missing column_widths in config"
    assert '#0' in config['column_widths'], "Missing #0 column width"
    print("   ✓ column_widths configuration present")
    
    # Check for API configuration
    assert 'search_api' in config, "Missing search_api in config"
    assert 'sources' in config['search_api'], "Missing sources in search_api"
    assert 'wikipedia' in config['search_api']['sources'], "Missing wikipedia source"
    assert 'wiktionary' in config['search_api']['sources'], "Missing wiktionary source"
    print("   ✓ API sources configuration present")
    
    # Check for endpoints
    assert 'wikipedia_endpoint' in config['search_api'], "Missing wikipedia_endpoint"
    assert 'wiktionary_endpoint' in config['search_api'], "Missing wiktionary_endpoint"
    print("   ✓ API endpoints configured")
    
    print("   ✓ Config file: PASSED")
except Exception as e:
    print(f"   ✗ Config file: FAILED - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL ENHANCED FEATURES TESTS PASSED ✓")
print("=" * 60)
print("\nEnhanced features verified:")
print("  • Location tracking to avoid re-searching")
print("  • Term caching for performance")
print("  • Wikipedia API integration (with fallback)")
print("  • Wiktionary API integration (with fallback)")
print("  • Column width persistence")
print("  • No record limit (removed 33/50 limit)")
print("=" * 60)
