#!/usr/bin/env python3
"""
Main entry point for MediaMind AI.
Enhanced media search engine with AI-powered analysis.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.search_engine import EnhancedMediaSearchEngine
from core.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="MediaMind AI - Enhanced Media Search Engine")
    parser.add_argument("--config", "-c", default="config.yaml", help="Configuration file path")
    parser.add_argument("--scan", "-s", nargs="+", help="Scan specific directories")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--web", "-w", action="store_true", help="Start web interface")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--full-scan", action="store_true", help="Force full scan (ignore incremental)")
    parser.add_argument("--reset-scan", action="store_true", help="Reset scan state")
    
    args = parser.parse_args()
    
    try:
        # Initialize search engine
        logger.info("Initializing MediaMind AI...")
        search_engine = EnhancedMediaSearchEngine(args.config)
        
        if args.setup:
            run_setup_wizard(search_engine)
        elif args.web:
            start_web_interface()
        elif args.scan:
            scan_directories(search_engine, args.scan, args.full_scan)
        elif args.query:
            search_media(search_engine, args.query)
        elif args.stats:
            show_statistics(search_engine)
        elif args.reset_scan:
            reset_scan_state(search_engine)
        else:
            # Interactive mode
            run_interactive_mode(search_engine)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

def run_setup_wizard(search_engine):
    """Run setup wizard for first-time configuration."""
    print("\n🧠 MediaMind AI Setup Wizard")
    print("=" * 50)
    
    # Check Ollama installation
    print("\n1. Checking Ollama installation...")
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        print("✅ Ollama is installed and running")
        
        # Check for required models
        available_models = [model['name'] for model in models['models']]
        required_models = ['llava:latest', 'llama3.1:latest']
        
        missing_models = []
        for model in required_models:
            if model not in available_models:
                missing_models.append(model)
        
        if missing_models:
            print(f"❌ Missing required models: {', '.join(missing_models)}")
            print("Please run the following commands:")
            for model in missing_models:
                print(f"  ollama pull {model}")
            return
        else:
            print("✅ All required models are available")
            
    except Exception as e:
        print(f"❌ Ollama not found or not running: {e}")
        print("Please install Ollama from https://ollama.com/")
        return
    
    # Configure scan paths
    print("\n2. Configuring scan paths...")
    current_paths = search_engine.config_loader.get('media.scan_paths', [])
    
    if current_paths:
        print("Current scan paths:")
        for i, path in enumerate(current_paths, 1):
            print(f"  {i}. {path}")
    
    print("\nEnter paths to scan for media files (one per line, empty line to finish):")
    new_paths = []
    while True:
        path = input("Path: ").strip()
        if not path:
            break
        if os.path.exists(path):
            new_paths.append(path)
            print(f"✅ Added: {path}")
        else:
            print(f"❌ Path does not exist: {path}")
    
    if new_paths:
        all_paths = current_paths + new_paths
        search_engine.update_scan_paths(all_paths)
        print(f"✅ Updated scan paths: {len(all_paths)} total")
    
    # Test scan
    print("\n3. Testing media discovery...")
    test_paths = search_engine.config_loader.get('media.scan_paths', [])
    if test_paths:
        media_files = search_engine.media_processor.discover_media_files(test_paths)
        print(f"✅ Found {len(media_files)} media files")
        
        if media_files:
            print("Sample files:")
            for file in media_files[:5]:
                print(f"  • {file}")
            if len(media_files) > 5:
                print(f"  ... and {len(media_files) - 5} more")
    else:
        print("❌ No scan paths configured")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Run: python main.py --scan  # to index your media files")
    print("2. Run: python main.py --web   # to start the web interface")

def start_web_interface():
    """Start the Streamlit web interface."""
    print("Starting web interface...")
    print("Open your browser and go to: http://localhost:8501")
    
    import subprocess
    import sys
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "web/app.py"])

def scan_directories(search_engine, directories, full_scan=False):
    """Scan specific directories for media files."""
    scan_type = "full" if full_scan else "incremental"
    print(f"Scanning directories ({scan_type}): {', '.join(directories)}")
    
    # Update scan paths
    search_engine.update_scan_paths(directories)
    
    # Scan and index
    result = search_engine.scan_and_index_media(directories, incremental=not full_scan)
    
    print(f"\nScan completed!")
    print(f"Processed: {result['processed']}")
    print(f"Skipped: {result['skipped']}")
    print(f"Errors: {result['errors']}")
    if 'deleted' in result:
        print(f"Deleted: {result['deleted']}")
    print(f"Total: {result.get('total', result['processed'] + result['skipped'] + result['errors'])}")

def search_media(search_engine, query):
    """Search for media files."""
    print(f"Searching for: {query}")
    
    # Perform semantic search
    results = search_engine.semantic_search(query, limit=10)
    
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['file_name']}")
        print(f"   Path: {result['file_path']}")
        print(f"   Type: {result['file_type']}")
        if result.get('ai_description'):
            print(f"   Description: {result['ai_description']}")
        if result.get('ai_tags'):
            print(f"   Tags: {', '.join(result['ai_tags'][:5])}")
        if 'similarity_score' in result:
            print(f"   Similarity: {result['similarity_score']:.2f}")

def show_statistics(search_engine):
    """Show system statistics."""
    stats = search_engine.get_scan_statistics()
    
    print("\n📊 MediaMind AI Statistics")
    print("=" * 30)
    print(f"Total files: {stats.get('total_files', 0)}")
    print(f"Database size: {stats.get('database_size', 0) / 1024 / 1024:.1f} MB")
    
    # Scan information
    scan_info = stats.get('scan_info', {})
    if scan_info.get('last_scan_time'):
        print(f"Last scan: {scan_info['last_scan_time']}")
    if scan_info.get('processed_files_count'):
        print(f"Processed files: {scan_info['processed_files_count']}")
    
    if stats.get('by_type'):
        print("\nFiles by type:")
        for file_type, count in stats['by_type'].items():
            print(f"  {file_type.title()}: {count}")
    
    if stats.get('top_tags'):
        print("\nTop tags:")
        for tag_info in stats['top_tags'][:10]:
            print(f"  {tag_info['tag']}: {tag_info['count']}")

def reset_scan_state(search_engine):
    """Reset scan state to force full scan next time."""
    print("Resetting scan state...")
    search_engine.reset_scan_state()
    print("✅ Scan state reset. Next scan will be a full scan.")

def run_interactive_mode(search_engine):
    """Run interactive mode."""
    print("\n🧠 MediaMind AI - Interactive Mode")
    print("=" * 40)
    print("Commands:")
    print("  search <query>  - Search for media files")
    print("  scan <path>     - Scan directory for media")
    print("  stats           - Show statistics")
    print("  web             - Start web interface")
    print("  quit            - Exit")
    print()
    
    while True:
        try:
            command = input("MediaMind> ").strip().split()
            if not command:
                continue
            
            if command[0] == "quit":
                break
            elif command[0] == "search":
                if len(command) > 1:
                    query = " ".join(command[1:])
                    search_media(search_engine, query)
                else:
                    print("Usage: search <query>")
            elif command[0] == "scan":
                if len(command) > 1:
                    path = command[1]
                    if os.path.exists(path):
                        scan_directories(search_engine, [path])
                    else:
                        print(f"Path does not exist: {path}")
                else:
                    print("Usage: scan <path>")
            elif command[0] == "stats":
                show_statistics(search_engine)
            elif command[0] == "web":
                start_web_interface()
                break
            else:
                print("Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
