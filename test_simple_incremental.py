#!/usr/bin/env python3
"""Simple test for incremental updates using persistent directory."""

import os
import tempfile
from pathlib import Path
from PIL import Image
import logging

from core.search_engine import EnhancedMediaSearchEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_media(test_dir):
    """Create test media files."""
    # Create subdirectories
    (test_dir / "photos").mkdir(exist_ok=True)
    (test_dir / "documents").mkdir(exist_ok=True)
    
    # Create test images
    img1 = Image.new('RGB', (800, 600), color='blue')
    img1.save(test_dir / "photos" / "ocean_scene.jpg")
    
    img2 = Image.new('RGB', (800, 600), color='green')
    img2.save(test_dir / "photos" / "nature_forest.jpg")
    
    # Create test document
    with open(test_dir / "documents" / "test_notes.txt", 'w') as f:
        f.write("This is a test document about nature and oceans.")
    
    logger.info(f"Created test media in {test_dir}")

def test_simple_incremental():
    """Test incremental updates with persistent directory."""
    print("🧪 Testing Simple Incremental Updates")
    print("=" * 50)
    
    # Use a persistent test directory
    test_dir = Path("test_media_simple")
    test_dir.mkdir(exist_ok=True)
    
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
        assert result3['processed'] == 1, f"Expected 1 new file, got {result3['processed']}"
        
        print("✅ Simple incremental update test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Clean up
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    test_simple_incremental()
