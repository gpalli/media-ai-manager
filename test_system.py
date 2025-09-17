#!/usr/bin/env python3
"""
Test script for MediaMind AI.
Tests the system with sample media files.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.search_engine import EnhancedMediaSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_media():
    """Create sample media files for testing."""
    test_dir = Path("test_media")
    test_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (test_dir / "photos").mkdir(exist_ok=True)
    (test_dir / "videos").mkdir(exist_ok=True)
    (test_dir / "documents").mkdir(exist_ok=True)
    
    # Create sample images
    print("Creating sample images...")
    
    # Image 1: Nature scene
    img1 = Image.new('RGB', (800, 600), color='green')
    img1.save(test_dir / "photos" / "nature_forest.jpg")
    
    # Image 2: Indoor scene
    img2 = Image.new('RGB', (800, 600), color='brown')
    img2.save(test_dir / "photos" / "indoor_room.jpg")
    
    # Image 3: People scene (simulated)
    img3 = Image.new('RGB', (800, 600), color='blue')
    img3.save(test_dir / "photos" / "people_group.jpg")
    
    # Create sample documents
    print("Creating sample documents...")
    
    # Text document
    with open(test_dir / "documents" / "ai_notes.txt", "w") as f:
        f.write("""
        Artificial Intelligence Notes
        
        This document contains notes about machine learning and AI.
        Topics covered:
        - Neural networks
        - Deep learning
        - Computer vision
        - Natural language processing
        
        Key concepts:
        - Supervised learning
        - Unsupervised learning
        - Reinforcement learning
        """)
    
    # Markdown document
    with open(test_dir / "documents" / "project_ideas.md", "w") as f:
        f.write("""
        # Project Ideas
        
        ## Media Management
        - AI-powered photo organization
        - Video content analysis
        - Document search and retrieval
        
        ## Machine Learning
        - Image classification
        - Text summarization
        - Recommendation systems
        
        ## Web Development
        - React applications
        - API development
        - Database design
        """)
    
    print(f"✅ Created test media in {test_dir}")
    return str(test_dir)

def test_media_discovery():
    """Test media file discovery."""
    print("\n🔍 Testing media discovery...")
    
    try:
        from core.media_processor import MediaProcessor
        from core.config_loader import ConfigLoader
        
        config = ConfigLoader()
        processor = MediaProcessor(config.config)
        
        test_dir = create_test_media()
        media_files = processor.discover_media_files([test_dir])
        
        print(f"✅ Found {len(media_files)} media files")
        for file in media_files:
            print(f"  • {file}")
        
        return media_files
        
    except Exception as e:
        print(f"❌ Media discovery test failed: {e}")
        return []

def test_media_processing():
    """Test media file processing."""
    print("\n⚙️ Testing media processing...")
    
    try:
        from core.media_processor import MediaProcessor
        from core.config_loader import ConfigLoader
        
        config = ConfigLoader()
        processor = MediaProcessor(config.config)
        
        test_dir = create_test_media()
        media_files = processor.discover_media_files([test_dir])
        
        if not media_files:
            print("❌ No media files found for processing test")
            return []
        
        # Process first few files
        processed_files = []
        for file_path in media_files[:3]:  # Process first 3 files
            media_file = processor.process_file(file_path)
            if media_file:
                processed_files.append(media_file)
                print(f"✅ Processed: {media_file.file_name} ({media_file.file_type})")
        
        return processed_files
        
    except Exception as e:
        print(f"❌ Media processing test failed: {e}")
        return []

def test_ai_analysis():
    """Test AI analysis (if Ollama is available)."""
    print("\n🤖 Testing AI analysis...")
    
    try:
        from core.ai_analyzer import AIMediaAnalyzer
        from core.config_loader import ConfigLoader
        
        config = ConfigLoader()
        analyzer = AIMediaAnalyzer(config.config)
        
        # Test with a simple image
        test_dir = create_test_media()
        test_image = test_dir + "/photos/nature_forest.jpg"
        
        if os.path.exists(test_image):
            from core.media_processor import MediaProcessor
            processor = MediaProcessor(config.config)
            media_file = processor.process_file(test_image)
            
            if media_file:
                # Test AI analysis
                analyzed_file = analyzer.analyze_media(media_file)
                print(f"✅ AI analysis completed for: {analyzed_file.file_name}")
                
                if analyzed_file.ai_description:
                    print(f"  Description: {analyzed_file.ai_description[:100]}...")
                if analyzed_file.ai_tags:
                    print(f"  Tags: {', '.join(analyzed_file.ai_tags[:5])}")
                
                return True
        
        print("❌ No test image found for AI analysis")
        return False
        
    except Exception as e:
        print(f"❌ AI analysis test failed: {e}")
        print("  This is expected if Ollama is not running or models are not installed")
        return False

def test_database():
    """Test database operations."""
    print("\n💾 Testing database operations...")
    
    try:
        from core.database_manager import DatabaseManager
        from core.config_loader import ConfigLoader
        
        config = ConfigLoader()
        db_manager = DatabaseManager(config.get('database', {}))
        
        # Test basic operations
        stats = db_manager.get_statistics()
        print(f"✅ Database initialized: {stats['total_files']} files")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_search_engine():
    """Test the complete search engine."""
    print("\n🔍 Testing search engine...")
    
    try:
        engine = EnhancedMediaSearchEngine()
        
        # Test basic functionality
        stats = engine.get_statistics()
        print(f"✅ Search engine initialized: {stats['total_files']} files")
        
        return True
        
    except Exception as e:
        print(f"❌ Search engine test failed: {e}")
        return False

def test_web_interface():
    """Test web interface imports."""
    print("\n🌐 Testing web interface...")
    
    try:
        import streamlit as st
        print("✅ Streamlit is available")
        
        # Test if we can import the web app
        sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))
        import app
        print("✅ Web application imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files."""
    test_dir = Path("test_media")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("✅ Cleaned up test files")

def main():
    """Run all tests."""
    print("🧠 MediaMind AI System Test")
    print("=" * 50)
    
    tests = [
        ("Media Discovery", test_media_discovery),
        ("Media Processing", test_media_processing),
        ("Database Operations", test_database),
        ("Search Engine", test_search_engine),
        ("Web Interface", test_web_interface),
        ("AI Analysis", test_ai_analysis),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result is not False
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Results Summary")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed. System should work with some limitations.")
    else:
        print("❌ Many tests failed. Please check the installation.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
