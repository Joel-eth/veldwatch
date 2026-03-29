# Contributing to Veldwatch

Thank you for considering contributing to Veldwatch! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/veldwatch`
3. Create a branch: `git checkout -b feat/your-feature`
4. Install dev dependencies: `pip install -e ".[dev]"`

## Development

### Running tests

```bash
pytest tests/ -v
```

### Linting

```bash
ruff check .
```

### Commit messages

Use semantic commit prefixes:
- `feat:` — new feature
- `fix:` — bug fix
- `chore:` — maintenance, dependencies
- `ci:` — CI/CD changes
- `docs:` — documentation only

## Pull Requests

1. Ensure all tests pass
2. Update documentation if needed
3. Use a descriptive PR title with a semantic prefix
4. Reference any related issues

## Code of Conduct

Be respectful and constructive. We're all here to build something useful.
