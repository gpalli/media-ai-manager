# 🚀 MediaMind AI - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### 1. Prerequisites
- Python 3.8+
- Internet connection (for downloading AI models)

### 2. Installation

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama
ollama serve

# 3. Install AI models (in another terminal)
ollama pull llava:latest
ollama pull llama3.1:latest

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Run setup wizard
python setup.py
```

### 3. Quick Test

```bash
# Test the system
python test_system.py

# Start web interface
python run.py web
```

### 4. Configure Scan Paths

Edit `config.yaml` and update the scan paths:

```yaml
media:
  scan_paths:
    - "/Users/yourname/Pictures"
    - "/Users/yourname/Desktop"
    - "/Users/yourname/Downloads"
```

### 5. Index Your Media

```bash
# Scan and index your media
python run.py scan

# Or scan specific directory
python run.py scan /path/to/your/photos
```

### 6. Search Your Media

```bash
# Search via command line
python run.py search "photos of mountains"

# Or use the web interface
python run.py web
# Then go to http://localhost:8501
```

## 🎯 Example Usage

### Web Interface
1. Run `python run.py web`
2. Open http://localhost:8501
3. Go to "Scan & Index" tab
4. Add your media directories
5. Click "Scan All Paths"
6. Go to "Search" tab
7. Search for "photos of people" or "outdoor scenes"

### Command Line
```bash
# Search for specific content
python main.py --query "videos from vacation"

# Scan new directories
python main.py --scan /path/to/new/photos

# Show statistics
python main.py --stats
```

## 🔧 Troubleshooting

### Common Issues

**"Ollama not found"**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

**"Model not found"**
```bash
# Pull required models
ollama pull llava:latest
ollama pull llama3.1:latest
```

**"No media files found"**
- Check scan paths in config.yaml
- Verify directories exist
- Check file format support

**"Slow processing"**
- Use smaller models: `llava:7b` instead of `llava:latest`
- Reduce batch size in config.yaml
- Limit file sizes

### Getting Help

1. Check the full README.md
2. Run `python test_system.py` to diagnose issues
3. Check logs for error messages
4. Ensure Ollama is running: `ollama list`

## 📁 Project Structure

```
media-ai-manager/
├── core/                    # Core modules
│   ├── config_loader.py    # Configuration management
│   ├── media_processor.py  # Media file processing
│   ├── ai_analyzer.py      # AI analysis with Ollama
│   ├── database_manager.py # Database and vector storage
│   └── search_engine.py    # Main search engine
├── web/                     # Web interface
│   └── app.py              # Streamlit web app
├── data/                    # Database and cache
├── cache/                   # Temporary files
├── config.yaml             # Configuration
├── requirements.txt        # Python dependencies
├── main.py                 # Main entry point
├── run.py                  # Simple launcher
├── setup.py                # Setup wizard
├── test_system.py          # System tests
└── README.md               # Full documentation
```

## 🎉 You're Ready!

Your MediaMind AI system is now ready to help you find and organize your media files with the power of AI!

For more detailed information, see the full README.md file.
