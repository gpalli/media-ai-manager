#!/usr/bin/env python3
"""
Simple launcher script for MediaMind AI.
Provides easy access to common operations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description="MediaMind AI Launcher")
    parser.add_argument("command", nargs="?", default="web", 
                       choices=["web", "scan", "search", "setup", "test", "help"],
                       help="Command to run")
    parser.add_argument("--path", "-p", help="Path for scan command")
    parser.add_argument("--query", "-q", help="Query for search command")
    
    args = parser.parse_args()
    
    if args.command == "web":
        start_web_interface()
    elif args.command == "scan":
        scan_media(args.path)
    elif args.command == "search":
        search_media(args.query)
    elif args.command == "setup":
        run_setup()
    elif args.command == "test":
        run_tests()
    elif args.command == "help":
        show_help()

def start_web_interface():
    """Start the web interface."""
    print("🌐 Starting MediaMind AI Web Interface...")
    print("Open your browser and go to: http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "main.py", "--web"])
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")

def scan_media(path=None):
    """Scan media files."""
    if path:
        print(f"📁 Scanning media in: {path}")
        subprocess.run([sys.executable, "main.py", "--scan", path])
    else:
        print("📁 Scanning all configured paths...")
        subprocess.run([sys.executable, "main.py", "--scan"])

def search_media(query=None):
    """Search media files."""
    if query:
        print(f"🔍 Searching for: {query}")
        subprocess.run([sys.executable, "main.py", "--query", query])
    else:
        print("🔍 Starting interactive search...")
        subprocess.run([sys.executable, "main.py"])

def run_setup():
    """Run setup wizard."""
    print("⚙️ Running MediaMind AI Setup...")
    subprocess.run([sys.executable, "setup.py"])

def run_tests():
    """Run system tests."""
    print("🧪 Running MediaMind AI Tests...")
    subprocess.run([sys.executable, "test_system.py"])

def show_help():
    """Show help information."""
    print("""
🧠 MediaMind AI - Enhanced Media Search Engine

USAGE:
    python run.py [command] [options]

COMMANDS:
    web         Start the web interface (default)
    scan        Scan media files
    search      Search media files
    setup       Run setup wizard
    test        Run system tests
    help        Show this help

EXAMPLES:
    python run.py                          # Start web interface
    python run.py web                      # Start web interface
    python run.py scan /path/to/photos     # Scan specific directory
    python run.py search "photos of cats"  # Search for media
    python run.py setup                    # Run setup wizard
    python run.py test                     # Run tests

For more information, see README.md
""")

if __name__ == "__main__":
    main()
