#!/usr/bin/env python3
"""Minimal test to debug database issues."""

import os
import tempfile
from pathlib import Path
from PIL import Image
import json

from core.config_loader import ConfigLoader
from core.media_processor import MediaProcessor, MediaFile
from core.database_manager import DatabaseManager

def test_minimal_database():
    """Test minimal database operations."""
    print("Testing minimal database operations...")
    
    # Initialize components
    config = ConfigLoader()._load_config()
    db_manager = DatabaseManager(config)
    media_processor = MediaProcessor(config)
    
    # Create a simple test file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        img = Image.new('RGB', (100, 100), color='red')
        img.save(tmp_file.name)
        test_file_path = tmp_file.name
    
    try:
        # Process the file
        print(f"Processing file: {test_file_path}")
        media_file = media_processor.process_file(test_file_path)
        
        if media_file:
            print(f"Media file created: {media_file.file_name}")
            print(f"AI tags: {media_file.ai_tags}")
            
            # Try to store in database
            print("Storing in database...")
            media_id = db_manager.store_media_file(media_file)
            print(f"Stored with ID: {media_id}")
            
        else:
            print("Failed to process file")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

if __name__ == "__main__":
    test_minimal_database()
