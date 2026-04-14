# Contributing to AI Sky Eye

First off, thank you for considering contributing to AI Sky Eye! It's people like you that make this project better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check if the issue already exists. When creating a bug report, please include:

- **Use a clear title**
- **Describe the bug** - What happened vs what you expected
- **Reproduce the bug** - Steps to reproduce
- **System info** - Windows version, Python version, AI Sky Eye version
- **Screenshots** - If applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear title**
- **Describe the enhancement** - What do you want to happen?
- **Explain why** - How would this benefit users?
- **List alternatives** - What else could solve this?

### Pull Requests

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Setup

### Prerequisites

- Windows 10/11
- Python 3.8+
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/your-username/ai-sky-eye.git
cd ai-sky-eye

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/screen_controller

# Run specific test
pytest tests/test_screen_controller.py::test_capture_screen
```

### Code Style

We use:
- **Black** for formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check style
flake8 src/ tests/
mypy src/screen_controller
```

## Project Structure

```
ai-sky-eye/
├── src/
│   └── screen_controller/    # Main package
│       ├── __init__.py
│       ├── screen_controller.py
│       ├── enhanced_ocr.py
│       ├── vision.py
│       ├── smart_brain.py
│       ├── learning.py
│       └── ai_agent.py
├── tests/                    # Test files
├── examples/                 # Example scripts
├── docs/                     # Documentation
└── assets/                   # Images and assets
```

## Writing Documentation

- Use clear, concise language
- Include code examples
- Update README.md if adding features
- Add docstrings to all public functions

## Commit Message Guidelines

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add voice control support

- Add VoiceAIAgent class
- Integrate SpeechRecognition
- Add voice command parsing
```

## Testing Guidelines

- Write tests for new features
- Maintain test coverage above 80%
- Use descriptive test names
- Group related tests in classes

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions on GitHub
- Contact maintainers

Thank you for contributing! 🦞
