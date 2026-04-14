# Changelog

All notable changes to AI Sky Eye will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline
- Automated testing on Python 3.8-3.11
- Security scanning with Bandit and Safety
- Code quality checks with pylint and radon
- Automated release workflow

## [2.5.0] - 2026-04-14

### Added
- **Smart Brain Module** - Intelligent decision making and context awareness
  - Screen context analysis (login, main, error, loading states)
  - Anomaly detection (errors, timeouts, crashes)
  - Intelligent decision making with retry logic
  - Learning from success/failure patterns

- **Learning Module** - Record, replay, and optimize workflows
  - Action recording with context
  - Flow replay with adaptive mode
  - Automatic flow optimization (remove redundancy, add waits)
  - Pattern learning from multiple executions

- **AI Agent Module** - Autonomous AI agent
  - Natural language task execution
  - Observe-think-act loop
  - Voice control support (VoiceAIAgent)
  - Auto-confirmation mode

- **Performance Module** - Caching and optimization
  - OCR engine caching
  - Screenshot caching with TTL
  - Element location caching
  - Performance monitoring
  - `@cached` decorator

- **Voice Control** - Speech recognition integration
  - VoiceAIAgent for voice commands
  - Interactive voice mode
  - Speech-to-text processing

- **Examples** - Comprehensive example suite
  - 01_basic_control.py - Screen control basics
  - 02_ocr_vision.py - OCR and vision features
  - 03_smart_brain.py - Smart brain usage
  - 04_learning_recording.py - Recording and learning
  - 05_ai_agent.py - AI agent capabilities
  - 06_performance.py - Performance optimization

- **Documentation**
  - Technical deep-dive blog post
  - Architecture diagrams
  - Logo and banner assets
  - Contributing guidelines

### Enhanced
- OCR multi-engine support (PaddleOCR, EasyOCR, Tesseract)
- Improved error handling and recovery
- Better type hints throughout codebase
- Enhanced documentation in README

## [2.0.0] - 2026-04-09

### Added
- Complete modular architecture rewrite
- Browser automation with Selenium integration
- Remote HTTP API for external control
- Task scheduling system
- Window management utilities
- Clipboard operations
- Enhanced screenshot capabilities
- UI element finder

### Changed
- Restructured package layout
- Improved API consistency
- Better error messages

## [1.0.0] - 2026-04-01

### Added
- Initial release
- Basic screen control (mouse, keyboard)
- Screenshot capture
- Basic OCR integration
- Core automation primitives

---

## Release Notes Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Security improvements
```
