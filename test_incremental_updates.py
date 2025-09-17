#!/usr/bin/env python3
"""
Test script for incremental update functionality.
Verifies that the system properly handles new, modified, and deleted files.
"""

import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from PIL import Image
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.search_engine import EnhancedMediaSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_media(test_dir: Path):
    """Create test media files."""
    # Create subdirectories
    (test_dir / "photos").mkdir(exist_ok=True)
    (test_dir / "documents").mkdir(exist_ok=True)
    
    # Create sample images
    img1 = Image.new('RGB', (800, 600), color='green')
    img1.save(test_dir / "photos" / "nature_forest.jpg")
    
    img2 = Image.new('RGB', (800, 600), color='blue')
    img2.save(test_dir / "photos" / "ocean_scene.jpg")
    
    # Create sample document
    with open(test_dir / "documents" / "test_notes.txt", "w") as f:
        f.write("This is a test document about nature and oceans.")
    
    logger.info(f"Created test media in {test_dir}")

def test_incremental_updates():
    """Test incremental update functionality."""
    print("🧪 Testing Incremental Updates")
    print("=" * 50)
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_media"
        test_dir.mkdir()
        
        try:
            # Initialize search engine
            print("1. Initializing search engine...")
            search_engine = EnhancedMediaSearchEngine()
            
            # Update scan paths to test directory
            search_engine.update_scan_paths([str(test_dir)])
            
            # Create initial media files
            print("2. Creating initial media files...")
            create_test_media(test_dir)
            
            # First scan - should process all files
            print("3. Running first scan (should process all files)...")
            result1 = search_engine.scan_and_index_media(incremental=True)
            print(f"   Result: {result1}")
            
            # Verify files were processed
            assert result1['processed'] > 0, "No files were processed in first scan"
            
            # Second scan - should skip all files (no changes)
            print("4. Running second scan (should skip all files)...")
            result2 = search_engine.scan_and_index_media(incremental=True)
            print(f"   Result: {result2}")
            
            # Verify no files were processed (correct behavior when no changes detected)
            assert result2['processed'] == 0, "Files were processed when no changes detected"
            # Note: When no changes are detected, there's nothing to skip
            
            # Add new file
            print("5. Adding new file...")
            img3 = Image.new('RGB', (800, 600), color='red')
            img3.save(test_dir / "photos" / "sunset.jpg")
            
            # Third scan - should process new file
            print("6. Running third scan (should process new file)...")
            result3 = search_engine.scan_and_index_media(incremental=True)
            print(f"   Result: {result3}")
            
            # Verify new file was processed
            assert result3['processed'] == 1, "New file was not processed"
            
            # Modify existing file
            print("7. Modifying existing file...")
            img1_modified = Image.new('RGB', (800, 600), color='darkgreen')
            img1_modified.save(test_dir / "photos" / "nature_forest.jpg")
            
            # Fourth scan - should process modified file
            print("8. Running fourth scan (should process modified file)...")
            result4 = search_engine.scan_and_index_media(incremental=True)
            print(f"   Result: {result4}")
            
            # Verify modified file was processed
            assert result4['processed'] == 1, "Modified file was not processed"
            
            # Move file
            print("9. Moving file...")
            old_path = test_dir / "photos" / "ocean_scene.jpg"
            new_path = test_dir / "documents" / "ocean_scene.jpg"
            shutil.move(str(old_path), str(new_path))
            
            # Fifth scan - should handle moved file
            print("10. Running fifth scan (should handle moved file)...")
            result5 = search_engine.scan_and_index_media(incremental=True)
            print(f"    Result: {result5}")
            
            # Verify moved file was handled
            assert result5['processed'] == 1, "Moved file was not processed"
            
            # Delete file
            print("11. Deleting file...")
            (test_dir / "documents" / "test_notes.txt").unlink()
            
            # Sixth scan - should handle deleted file
            print("12. Running sixth scan (should handle deleted file)...")
            result6 = search_engine.scan_and_index_media(incremental=True)
            print(f"    Result: {result6}")
            
            # Verify deleted file was handled
            assert result6['deleted'] == 1, "Deleted file was not handled"
            
            # Test full scan
            print("13. Running full scan...")
            result7 = search_engine.force_full_scan()
            print(f"    Result: {result7}")
            
            # Verify full scan processed files
            assert result7['processed'] > 0, "Full scan did not process files"
            
            print("\n✅ All incremental update tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_scan_statistics():
    """Test scan statistics functionality."""
    print("\n📊 Testing Scan Statistics")
    print("=" * 30)
    
    try:
        search_engine = EnhancedMediaSearchEngine()
        stats = search_engine.get_scan_statistics()
        
        print(f"Total files: {stats.get('total_files', 0)}")
        print(f"Database size: {stats.get('database_size', 0) / 1024 / 1024:.1f} MB")
        
        scan_info = stats.get('scan_info', {})
        print(f"Last scan: {scan_info.get('last_scan_time', 'Never')}")
        print(f"Processed files: {scan_info.get('processed_files_count', 0)}")
        
        print("✅ Scan statistics test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Scan statistics test failed: {e}")
        return False

def test_file_hash_consistency():
    """Test that file hashing is consistent."""
    print("\n🔍 Testing File Hash Consistency")
    print("=" * 35)
    
    try:
        from core.media_processor import MediaProcessor
        from core.config_loader import ConfigLoader
        
        config = ConfigLoader()
        processor = MediaProcessor(config.config)
        
        # Create a test file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"Test content for hashing")
            test_file = f.name
        
        try:
            # Calculate hash multiple times
            hash1 = processor._calculate_file_hash(test_file)
            hash2 = processor._calculate_file_hash(test_file)
            
            assert hash1 == hash2, "File hash is not consistent"
            assert len(hash1) == 64, "File hash is not 64 characters (SHA-256)"
            
            print("✅ File hash consistency test passed!")
            return True
            
        finally:
            os.unlink(test_file)
            
    except Exception as e:
        print(f"❌ File hash consistency test failed: {e}")
        return False

def main():
    """Run all incremental update tests."""
    print("🧠 MediaMind AI - Incremental Update Tests")
    print("=" * 60)
    
    tests = [
        ("File Hash Consistency", test_file_hash_consistency),
        ("Incremental Updates", test_incremental_updates),
        ("Scan Statistics", test_scan_statistics),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All incremental update tests passed!")
        print("\nThe system properly handles:")
        print("  • New files - detected and processed")
        print("  • Modified files - detected and reprocessed")
        print("  • Moved files - detected and updated")
        print("  • Deleted files - detected and removed")
        print("  • Incremental scanning - only processes changes")
        print("  • Full scanning - processes all files when needed")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
