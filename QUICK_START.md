# 🚀 Quick Start Guide

Get MediaMind AI up and running in 5 minutes!

## Prerequisites

- **Python 3.8+**
- **Ollama** installed and running
- **Git** (for cloning)

## 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/gpalli/media-ai-manager.git
cd media-ai-manager

# Create virtual environment
python -m venv media-ai-manager
source media-ai-manager/bin/activate  # On Windows: media-ai-manager\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Install Ollama & Models

```bash
# Install Ollama (if not installed)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve

# Pull required models (in another terminal)
ollama pull llama3.1:latest
```

## 3. Configure & Test

```bash
# Run setup wizard
python main.py --setup

# Test with sample media
mkdir test_media
# Add some photos to test_media/

# Scan and index
python main.py --scan test_media

# Search
python main.py --query "nature"
```

## 4. Start Web Interface

```bash
# Start the web UI
streamlit run web/app.py
```

Open your browser to `http://localhost:8501`

## 🎯 What's Next?

- **Add your media**: Update `config.yaml` with your photo/video directories
- **Explore features**: Use the web interface to search and organize
- **Read the docs**: Check out [README.md](README.md) for detailed documentation

## 🆘 Need Help?

- Check [troubleshooting](README.md#troubleshooting) in the main README
- Open an [issue](https://github.com/gpalli/media-ai-manager/issues) on GitHub
- Read the [contributing guide](CONTRIBUTING.md)

---

**Happy searching! 🧠✨**