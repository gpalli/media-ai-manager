# Contributing to MediaMind AI

Thank you for your interest in contributing to MediaMind AI! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists
2. Search the closed issues as well
3. Provide as much detail as possible

When creating an issue, please include:
- **Operating System** and version
- **Python version**
- **Ollama version** and models installed
- **Error messages** (if any)
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior

### Suggesting Features

We welcome feature suggestions! Please:
1. Check if the feature has been requested before
2. Provide a clear description of the feature
3. Explain why it would be useful
4. Consider if it fits with the project's goals

### Code Contributions

#### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/media-ai-manager.git
   cd media-ai-manager
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv media-ai-manager
   source media-ai-manager/bin/activate  # On Windows: media-ai-manager\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Guidelines

##### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

##### Testing
- Test your changes thoroughly
- Run existing tests: `python test_simple_incremental.py`
- Add tests for new functionality when possible

##### Documentation
- Update README.md if you add new features
- Add docstrings to new functions
- Update comments for complex code sections

#### Submitting Changes

1. **Test your changes**:
   ```bash
   python test_simple_incremental.py
   python main.py --stats
   ```

2. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub

### Pull Request Guidelines

#### Before Submitting
- [ ] Code follows the project's style guidelines
- [ ] Changes are tested and working
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive

#### Pull Request Template
When creating a PR, please include:
- **Description**: What changes were made and why
- **Type**: Bug fix, feature, documentation, etc.
- **Testing**: How the changes were tested
- **Breaking Changes**: Any breaking changes (if applicable)

## 🏗️ Project Structure

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
├── data/                    # Database and cache (auto-created)
├── config.yaml             # Configuration file
├── main.py                 # Command-line interface
├── requirements.txt        # Python dependencies
└── tests/                  # Test files
    ├── test_simple_incremental.py
    └── test_incremental_updates.py
```

## 🧪 Testing

### Running Tests
```bash
# Run incremental update tests
python test_simple_incremental.py
python test_incremental_updates.py

# Test the main application
python main.py --stats
python main.py --query "test"
```

### Creating Tests
When adding new features, consider adding tests:
- Unit tests for individual functions
- Integration tests for complete workflows
- Performance tests for critical paths

## 📝 Code Review Process

1. **Automated Checks**: GitHub Actions will run basic checks
2. **Manual Review**: Maintainers will review the code
3. **Feedback**: Address any feedback from reviewers
4. **Merge**: Once approved, the PR will be merged

## 🐛 Bug Reports

When reporting bugs, please include:

### System Information
- Operating System (macOS, Windows, Linux)
- Python version (`python --version`)
- Ollama version (`ollama --version`)
- Installed models (`ollama list`)

### Error Details
- Complete error message
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)

### Logs
- Console output
- Any log files generated
- Database errors (if any)

## 💡 Feature Requests

When suggesting features:

1. **Check existing issues** first
2. **Describe the feature** clearly
3. **Explain the use case** and benefits
4. **Consider implementation** complexity
5. **Think about alternatives** or workarounds

## 🏷️ Labels

We use labels to categorize issues and PRs:
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## 📞 Getting Help

If you need help:
1. Check the [README.md](README.md) for setup instructions
2. Look through existing [Issues](https://github.com/gpalli/media-ai-manager/issues)
3. Create a new issue with your question
4. Join discussions in the [Discussions](https://github.com/gpalli/media-ai-manager/discussions) section

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to MediaMind AI! 🎉
