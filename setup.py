#!/usr/bin/env python3
"""
Setup script for MediaMind AI.
Handles installation and initial configuration.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_ollama_installation():
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Ollama is not installed or not running")
    return False

def install_ollama():
    """Install Ollama based on the operating system."""
    system = platform.system().lower()
    
    print("Installing Ollama...")
    
    if system == "darwin":  # macOS
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh'], 
                          check=True, stdout=subprocess.PIPE)
            subprocess.run(['sh', '-c', 'curl -fsSL https://ollama.com/install.sh | sh'], 
                          check=True)
            print("✅ Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Ollama automatically")
            print("Please install manually from https://ollama.com/")
            return False
    
    elif system == "linux":
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh'], 
                          check=True, stdout=subprocess.PIPE)
            subprocess.run(['sh', '-c', 'curl -fsSL https://ollama.com/install.sh | sh'], 
                          check=True)
            print("✅ Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Ollama automatically")
            print("Please install manually from https://ollama.com/")
            return False
    
    elif system == "windows":
        print("❌ Windows installation not supported in this script")
        print("Please download and install from https://ollama.com/download")
        return False
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def start_ollama_service():
    """Start Ollama service."""
    print("Starting Ollama service...")
    try:
        # Check if Ollama is already running
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama service is already running")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Start Ollama service in background
    try:
        if platform.system().lower() == "windows":
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        # Wait a moment for service to start
        import time
        time.sleep(3)
        
        # Verify service is running
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama service started successfully")
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Ollama service: {e}")
        return False

def install_required_models():
    """Install required Ollama models."""
    models = [
        'llava:latest',      # Vision model
        'llama3.1:latest'    # Text model
    ]
    
    print("Installing required AI models...")
    print("This may take a while depending on your internet connection...")
    
    for model in models:
        print(f"Installing {model}...")
        try:
            result = subprocess.run(['ollama', 'pull', model], 
                                  capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"✅ {model} installed successfully")
            else:
                print(f"❌ Failed to install {model}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout installing {model}")
            return False
        except Exception as e:
            print(f"❌ Error installing {model}: {e}")
            return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ['data', 'cache', 'cache/thumbnails', 'templates', 'web']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_installation():
    """Test the installation."""
    print("Testing installation...")
    
    try:
        # Test imports
        from core.search_engine import EnhancedMediaSearchEngine
        print("✅ Core modules import successfully")
        
        # Test configuration
        from core.config_loader import ConfigLoader
        config = ConfigLoader()
        print("✅ Configuration loaded successfully")
        
        # Test Ollama connection
        import ollama
        client = ollama.Client()
        models = client.list()
        print(f"✅ Ollama connection successful ({len(models['models'])} models available)")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def create_sample_config():
    """Create a sample configuration file."""
    config_path = "config.yaml"
    if os.path.exists(config_path):
        print("✅ Configuration file already exists")
        return True
    
    sample_config = {
        'app': {
            'name': 'MediaMind AI',
            'version': '2.0.0',
            'debug': True
        },
        'media': {
            'supported_formats': {
                'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic'],
                'videos': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
                'documents': ['.pdf', '.docx', '.pptx', '.txt', '.md']
            },
            'max_file_size_mb': 500,
            'scan_paths': [
                os.path.expanduser("~/Pictures"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Downloads")
            ],
            'excluded_paths': ['/System', '/Library', '/.Trash', '/node_modules', '/.git'],
            'parallel_workers': 4,
            'batch_size': 8
        },
        'search': {
            'embedding_model': 'sentence-transformers/msmarco-bert-base-dot-v5',
            'faiss_dimension': 768,
            'chunk_size': 500,
            'chunk_overlap': 50,
            'max_results': 20,
            'similarity_threshold': 0.7
        },
        'ollama': {
            'base_url': 'http://localhost:11434',
            'vision_model': 'llava:latest',
            'text_model': 'llama3.1:latest',
            'timeout': 120,
            'vision_analysis': {
                'enabled': True,
                'generate_descriptions': True,
                'extract_tags': True,
                'detect_objects': True,
                'analyze_scenes': True,
                'extract_text': True
            }
        },
        'database': {
            'type': 'sqlite',
            'path': './data/mediadb.sqlite',
            'vector_store': './data/faiss_index',
            'backup_enabled': True,
            'backup_interval_hours': 24
        },
        'web': {
            'host': 'localhost',
            'port': 8501,
            'title': 'MediaMind AI - Local Media Search Engine',
            'debug': True
        },
        'performance': {
            'cache_size_mb': 1024,
            'thumbnail_cache_days': 30,
            'enable_gpu': False,
            'batch_processing': True
        }
    }
    
    try:
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)
        print("✅ Sample configuration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("🧠 MediaMind AI Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Setup failed at Python dependencies")
        sys.exit(1)
    
    # Check Ollama installation
    if not check_ollama_installation():
        print("\nInstalling Ollama...")
        if not install_ollama():
            print("❌ Setup failed at Ollama installation")
            sys.exit(1)
    
    # Start Ollama service
    if not start_ollama_service():
        print("❌ Setup failed at starting Ollama service")
        sys.exit(1)
    
    # Install required models
    if not install_required_models():
        print("❌ Setup failed at installing AI models")
        sys.exit(1)
    
    # Create sample configuration
    if not create_sample_config():
        print("❌ Setup failed at creating configuration")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Setup failed at testing installation")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure scan paths in config.yaml")
    print("2. Run: python main.py --scan  # to index your media")
    print("3. Run: python main.py --web   # to start the web interface")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
