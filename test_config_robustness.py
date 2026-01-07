#!/usr/bin/env python3
"""
Test script to verify config handling robustness.
Tests various edge cases and error conditions for configuration loading.
"""
import os
import sys
import json
import tempfile
from database import DatabaseManager

print("=" * 70)
print("Configuration Robustness Test Suite")
print("=" * 70)

# Test 1: Missing config file
print("\n1. Testing with non-existent config file...")
try:
    db = DatabaseManager('nonexistent_config.json')
    print(f"   ✓ Handled missing config gracefully")
    print(f"   ✓ Data directory: {db.data_dir}")
    print(f"   ✓ Database path: {db.db_path}")
    assert 'Data' in db.data_dir
    assert 'british_slang.db' in db.db_path
    print("   ✓ Test 1 PASSED")
except Exception as e:
    print(f"   ✗ Test 1 FAILED: {e}")
    sys.exit(1)

# Test 2: Incomplete config (missing data_directory key)
print("\n2. Testing with incomplete config (missing data_directory)...")
try:
    # Create temporary incomplete config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'database_name': 'test.db',
            'window_title': 'Test'
        }, f)
        temp_config = f.name
    
    db = DatabaseManager(temp_config)
    print(f"   ✓ Handled incomplete config gracefully")
    print(f"   ✓ Data directory: {db.data_dir}")
    print(f"   ✓ Database path: {db.db_path}")
    assert 'Data' in db.data_dir, "Should use default data_directory"
    assert 'test.db' in db.db_path, "Should preserve custom database_name"
    print("   ✓ Test 2 PASSED")
    os.unlink(temp_config)
except Exception as e:
    print(f"   ✗ Test 2 FAILED: {e}")
    if 'temp_config' in locals():
        os.unlink(temp_config)
    sys.exit(1)

# Test 3: Malformed JSON
print("\n3. Testing with malformed JSON...")
try:
    # Create temporary malformed config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{ "database_name": "test.db", invalid json }')
        temp_config = f.name
    
    db = DatabaseManager(temp_config)
    print(f"   ✓ Handled malformed JSON gracefully")
    print(f"   ✓ Data directory: {db.data_dir}")
    print(f"   ✓ Database path: {db.db_path}")
    assert 'Data' in db.data_dir
    assert 'british_slang.db' in db.db_path
    print("   ✓ Test 3 PASSED")
    os.unlink(temp_config)
except Exception as e:
    print(f"   ✗ Test 3 FAILED: {e}")
    if 'temp_config' in locals():
        os.unlink(temp_config)
    sys.exit(1)

# Test 4: Empty config file
print("\n4. Testing with empty config...")
try:
    # Create temporary empty config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        temp_config = f.name
    
    db = DatabaseManager(temp_config)
    print(f"   ✓ Handled empty config gracefully")
    print(f"   ✓ Data directory: {db.data_dir}")
    print(f"   ✓ Database path: {db.db_path}")
    assert 'Data' in db.data_dir
    assert 'british_slang.db' in db.db_path
    print("   ✓ Test 4 PASSED")
    os.unlink(temp_config)
except Exception as e:
    print(f"   ✗ Test 4 FAILED: {e}")
    if 'temp_config' in locals():
        os.unlink(temp_config)
    sys.exit(1)

# Test 5: Config passed directly (no file)
print("\n5. Testing with config passed directly (config sharing)...")
try:
    custom_config = {
        'data_directory': 'CustomTestData',
        'database_name': 'custom_test.db',
        'window_title': 'Custom App'
    }
    
    db = DatabaseManager(config=custom_config)
    print(f"   ✓ Handled direct config passing")
    print(f"   ✓ Data directory: {db.data_dir}")
    print(f"   ✓ Database path: {db.db_path}")
    assert 'CustomTestData' in db.data_dir, "Should use custom data_directory"
    assert 'custom_test.db' in db.db_path, "Should use custom database_name"
    print("   ✓ Test 5 PASSED")
except Exception as e:
    print(f"   ✗ Test 5 FAILED: {e}")
    sys.exit(1)

# Test 6: Complete valid config
print("\n6. Testing with complete valid config...")
try:
    # Create temporary complete config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'data_directory': 'ValidTestData',
            'database_name': 'valid_test.db',
            'window_title': 'Valid Test App',
            'window_width': 1024,
            'window_height': 768
        }, f)
        temp_config = f.name
    
    db = DatabaseManager(temp_config)
    print(f"   ✓ Handled complete config correctly")
    print(f"   ✓ Data directory: {db.data_dir}")
    print(f"   ✓ Database path: {db.db_path}")
    assert 'ValidTestData' in db.data_dir
    assert 'valid_test.db' in db.db_path
    print("   ✓ Test 6 PASSED")
    os.unlink(temp_config)
except Exception as e:
    print(f"   ✗ Test 6 FAILED: {e}")
    if 'temp_config' in locals():
        os.unlink(temp_config)
    sys.exit(1)

# Test 7: Data directory creation
print("\n7. Testing data directory creation...")
try:
    import shutil
    test_data_dir = 'TestDirectoryCreation'
    
    # Make sure it doesn't exist
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    
    custom_config = {
        'data_directory': test_data_dir,
        'database_name': 'test.db'
    }
    
    db = DatabaseManager(config=custom_config)
    print(f"   ✓ Data directory created automatically")
    print(f"   ✓ Directory exists: {os.path.exists(test_data_dir)}")
    assert os.path.exists(test_data_dir), "Data directory should be created"
    assert os.path.isdir(test_data_dir), "Should be a directory"
    print("   ✓ Test 7 PASSED")
    
    # Cleanup
    shutil.rmtree(test_data_dir)
except Exception as e:
    print(f"   ✗ Test 7 FAILED: {e}")
    sys.exit(1)

# Test 8: Database operations with custom config
print("\n8. Testing database operations with custom config...")
try:
    import shutil
    test_data_dir = 'TestDBOperations'
    
    # Clean up if exists
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    
    custom_config = {
        'data_directory': test_data_dir,
        'database_name': 'operations_test.db'
    }
    
    db = DatabaseManager(config=custom_config)
    
    # Add a test term
    success, term_id = db.add_term(
        'test_term',
        'Test definition',
        'Test example',
        'test_category',
        'test_source'
    )
    
    print(f"   ✓ Database operations work correctly")
    print(f"   ✓ Term added: {success}, ID: {term_id}")
    
    # Get stats
    stats = db.get_database_stats()
    print(f"   ✓ Database stats: {stats['total_terms']} term(s)")
    assert stats['total_terms'] == 1, "Should have 1 term"
    print("   ✓ Test 8 PASSED")
    
    # Cleanup
    shutil.rmtree(test_data_dir)
except Exception as e:
    print(f"   ✗ Test 8 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL ROBUSTNESS TESTS PASSED ✓")
print("=" * 70)
print("\nSummary:")
print("  ✓ Missing config file handling")
print("  ✓ Incomplete config handling (missing keys)")
print("  ✓ Malformed JSON handling")
print("  ✓ Empty config handling")
print("  ✓ Direct config passing (config sharing)")
print("  ✓ Complete valid config handling")
print("  ✓ Automatic data directory creation")
print("  ✓ Database operations with custom config")
print("\nThe application is now robust against configuration errors!")
print("=" * 70)
