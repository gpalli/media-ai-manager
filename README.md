# 🧠 MediaMind AI - Enhanced Media Search Engine

[![GitHub](https://img.shields.io/badge/GitHub-gpalli%2Fmedia--ai--manager-blue?style=flat-square&logo=github)](https://github.com/gpalli/media-ai-manager)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-green?style=flat-square)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

An intelligent local media search engine that uses AI to help you find and organize your photos, videos, and documents. Based on the excellent [Towards AI implementation](https://pub.towardsai.net/building-your-own-generative-search-engine-for-local-files-using-open-source-models-b09af871751c) but enhanced specifically for media files.

> **🌟 Star this repository** if you find it useful!

## ✨ Features

- **🤖 AI-Powered Search**: Use natural language to find your media files
- **📸 Smart Analysis**: Automatically generates descriptions, tags, and metadata for images and videos
- **📁 Multiple File Types**: Supports images, videos, and documents (PDF, DOCX, PPTX, TXT)
- **🔒 Local Processing**: All analysis happens on your computer for complete privacy
- **📚 Collections**: Save and organize your search results
- **🔍 Similarity Search**: Find similar media files using AI
- **🌐 Web Interface**: Modern, responsive web UI built with Streamlit
- **⚡ Fast Search**: Vector-based similarity search using FAISS

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running
3. **Required AI models** pulled

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/gpalli/media-ai-manager.git
   cd media-ai-manager
   ```

2. **Install Ollama** (if not already installed)
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Windows
   # Download from https://ollama.com/download
   ```

3. **Pull required AI models**
   ```bash
   ollama pull llava:latest      # For image/video analysis
   ollama pull llama3.1:latest   # For text generation
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run setup wizard**
   ```bash
   python main.py --setup
   ```

### Basic Usage

1. **Start the web interface**
   ```bash
   python main.py --web
   ```
   Then open your browser to `http://localhost:8501`

2. **Or use command line**
   ```bash
   # Scan directories for media
   python main.py --scan /path/to/your/photos /path/to/your/videos
   
   # Search for media
   python main.py --query "photos of mountains"
   
   # Show statistics
   python main.py --stats
   ```

## 📖 Detailed Setup Guide

### Step 1: Install Ollama and Models

1. **Install Ollama**:
   - Visit [ollama.com](https://ollama.com) and download for your platform
   - Or use the command line installer:
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

3. **Pull required models** (this may take a while):
   ```bash
   # Vision model for image/video analysis
   ollama pull llava:latest
   
   # Text model for descriptions and answers
   ollama pull llama3.1:latest
   
   # Optional: smaller models for faster processing
   ollama pull llava:7b
   ollama pull llama3.1:8b
   ```

### Step 2: Configure MediaMind AI

1. **Edit configuration** (optional):
   ```bash
   nano config.yaml
   ```
   
   Key settings to customize:
   - `media.scan_paths`: Directories to scan for media
   - `media.max_file_size_mb`: Maximum file size to process
   - `ollama.vision_model`: Vision model to use
   - `ollama.text_model`: Text model to use

2. **Run setup wizard**:
   ```bash
   python main.py --setup
   ```
   
   This will:
   - Check Ollama installation
   - Verify required models
   - Configure scan paths
   - Test media discovery

### Step 3: Index Your Media

1. **Add scan paths** in the web interface or config file
2. **Start scanning**:
   ```bash
   python main.py --scan
   ```
   
   Or use the web interface:
   - Go to "Scan & Index" tab
   - Click "Scan All Paths"

3. **Monitor progress** - the system will:
   - Discover all media files
   - Extract metadata (EXIF, file properties)
   - Generate AI descriptions and tags
   - Create searchable embeddings

## 🎯 Testing with Sample Media

### Quick Test Setup

1. **Create test directories**:
   ```bash
   mkdir -p test_media/{photos,videos,documents}
   ```

2. **Add sample files**:
   - Copy some photos to `test_media/photos/`
   - Copy some videos to `test_media/videos/`
   - Copy some documents to `test_media/documents/`

3. **Configure scan paths**:
   ```bash
   python main.py --scan test_media
   ```

4. **Test search**:
   ```bash
   python main.py --query "photos of people"
   ```

### Sample Search Queries

Try these example searches:

- **"photos of people"** - Find images with people
- **"outdoor scenes"** - Find outdoor images
- **"videos from last year"** - Find recent videos
- **"documents about AI"** - Find AI-related documents
- **"images with text"** - Find images containing text
- **"nature photos"** - Find nature-related images

## 🔧 Configuration

### Main Configuration File (`config.yaml`)

```yaml
# Media file settings
media:
  supported_formats:
    images: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic']
    videos: ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    documents: ['.pdf', '.docx', '.pptx', '.txt', '.md']
  
  scan_paths:
    - "/Users/yourname/Pictures"
    - "/Users/yourname/Desktop"
    - "/Users/yourname/Downloads"
  
  max_file_size_mb: 500

# AI settings
ollama:
  base_url: "http://localhost:11434"
  vision_model: "llava:latest"
  text_model: "llama3.1:latest"
  timeout: 120

# Search settings
search:
  embedding_model: "sentence-transformers/msmarco-bert-base-dot-v5"
  max_results: 20
  similarity_threshold: 0.7
```

### Customizing Scan Paths

**Via Web Interface**:
1. Go to "Scan & Index" tab
2. Add new paths in the sidebar
3. Click "Scan All Paths"

**Via Command Line**:
```bash
python main.py --scan /path/to/photos /path/to/videos
```

**Via Config File**:
Edit `config.yaml` and update the `media.scan_paths` section.

## 🎨 Web Interface

The web interface provides a modern, user-friendly way to interact with MediaMind AI:

### Main Features

1. **🔍 Search Tab**:
   - Natural language search
   - Advanced filters (file type, date, scene type)
   - Semantic and text search options
   - Quick search examples

2. **📊 Scan & Index Tab**:
   - Configure scan paths
   - Start/stop scanning
   - View scan progress and results
   - Manage scan directories

3. **📁 Collections Tab**:
   - Create and manage collections
   - Save search results
   - Organize media files

4. **ℹ️ About Tab**:
   - System information
   - Usage instructions
   - Technology details

### Using the Search Interface

1. **Enter a search query** in natural language
2. **Choose search type**:
   - Semantic Search: AI-powered meaning-based search
   - Text Search: Traditional keyword search
   - Tag Search: Search by AI-generated tags
3. **Apply filters** if needed (file type, date range, etc.)
4. **Click Search** to find results
5. **View results** with thumbnails, descriptions, and tags
6. **Take actions**:
   - Open file location
   - Find similar media
   - Add to collection

## 🛠️ Advanced Usage

### Command Line Interface

```bash
# Basic commands
python main.py --help                    # Show help
python main.py --setup                   # Run setup wizard
python main.py --web                     # Start web interface
python main.py --stats                   # Show statistics

# Scanning
python main.py --scan /path/to/media     # Scan specific directory
python main.py --scan /path1 /path2      # Scan multiple directories

# Searching
python main.py --query "your search"     # Search for media

# Interactive mode
python main.py                           # Start interactive mode
```

### Interactive Mode

Start interactive mode for a command-line interface:

```bash
python main.py
```

Available commands:
- `search <query>` - Search for media
- `scan <path>` - Scan directory
- `stats` - Show statistics
- `web` - Start web interface
- `quit` - Exit

### API Usage

You can also use MediaMind AI programmatically:

```python
from core.search_engine import EnhancedMediaSearchEngine

# Initialize
engine = EnhancedMediaSearchEngine()

# Scan media
result = engine.scan_and_index_media(['/path/to/media'])

# Search
results = engine.semantic_search("photos of mountains")

# Generate AI answer
answer = engine.generate_answer("What photos do I have of nature?")
```

## 🔍 Search Capabilities

### Natural Language Search

MediaMind AI understands natural language queries:

- **"photos of my family"** - Finds images with people
- **"videos from vacation"** - Finds vacation-related videos
- **"documents about machine learning"** - Finds ML-related documents
- **"outdoor scenes"** - Finds outdoor images
- **"images with text"** - Finds images containing text

### AI-Generated Metadata

For each media file, the system generates:

- **Description**: Detailed description of the content
- **Tags**: Relevant keywords and categories
- **Objects**: Detected objects in images/videos
- **Scene Type**: Indoor/outdoor, nature/urban, etc.
- **Extracted Text**: Any text visible in images

### Search Types

1. **Semantic Search**: Uses AI to understand meaning
2. **Text Search**: Traditional keyword matching
3. **Tag Search**: Search by AI-generated tags
4. **Similarity Search**: Find similar media files

## 📊 Performance and Optimization

### System Requirements

- **RAM**: 8GB+ recommended (4GB minimum)
- **Storage**: 1GB+ for models and database
- **CPU**: Multi-core recommended for faster processing

### Optimization Tips

1. **Use smaller models** for faster processing:
   ```yaml
   ollama:
     vision_model: "llava:7b"
     text_model: "llama3.1:8b"
   ```

2. **Limit file sizes** in config:
   ```yaml
   media:
     max_file_size_mb: 100  # Smaller limit
   ```

3. **Reduce batch sizes** for limited RAM:
   ```yaml
   media:
     batch_size: 4  # Smaller batches
   ```

### Monitoring Performance

Check system statistics:
```bash
python main.py --stats
```

Or in the web interface:
- Go to "Scan & Index" tab
- View statistics in the sidebar

## 🐛 Troubleshooting

### Common Issues

1. **"Ollama not found"**
   - Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
   - Start Ollama: `ollama serve`

2. **"Model not found"**
   - Pull required models: `ollama pull llava:latest`
   - Check available models: `ollama list`

3. **"No media files found"**
   - Check scan paths in config
   - Verify directories exist
   - Check file format support

4. **"Slow processing"**
   - Use smaller models
   - Reduce batch size
   - Limit file sizes

5. **"Memory errors"**
   - Reduce batch size
   - Use smaller models
   - Close other applications

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py --web
```

### Log Files

Check logs for detailed error information:
- Console output shows real-time logs
- Database errors are logged to console
- FAISS index errors are logged to console

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/media-ai-manager.git
   cd media-ai-manager
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Make your changes** and test them
6. **Commit your changes**:
   ```bash
   git commit -m "Add: your feature description"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

### Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run tests**:
   ```bash
   python test_simple_incremental.py
   python test_incremental_updates.py
   ```

3. **Format code** (if you have the tools):
   ```bash
   black .
   isort .
   ```

### Project Structure

```
media-ai-manager/
├── core/                    # Core functionality
│   ├── config_loader.py    # Configuration management
│   ├── media_processor.py  # Media file processing
│   ├── ai_analyzer.py      # AI analysis with Ollama
│   ├── database_manager.py # Database operations
│   ├── search_engine.py    # Search functionality
│   └── incremental_updater.py # Incremental updates
├── web/                     # Web interface
│   └── app.py              # Streamlit application
├── data/                    # Database and cache
├── config.yaml             # Configuration file
├── main.py                 # Command-line interface
└── requirements.txt        # Python dependencies
```

### Based On

This project is based on the excellent work from:
- [Towards AI: Building Your Own Generative Search Engine](https://pub.towardsai.net/building-your-own-generative-search-engine-for-local-files-using-open-source-models-b09af871751c)
- [Ollama](https://ollama.com/) for local AI models
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [Sentence Transformers](https://www.sbert.net/) for embeddings

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Towards AI** for the original implementation
- **Ollama** for local AI model support
- **FAISS** for efficient vector search
- **Streamlit** for the web interface
- **Sentence Transformers** for text embeddings

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify Ollama is running and models are available

For additional help, please open an issue with:
- Your operating system
- Python version
- Error messages
- Steps to reproduce the issue

---

**Happy searching! 🧠✨**
