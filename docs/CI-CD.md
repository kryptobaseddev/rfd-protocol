# RFD Protocol CI/CD Documentation

## Overview

The RFD Protocol uses modern CI/CD practices with GitHub Actions, semantic versioning, and automated releases to ensure code quality and reliable deployments.

## 🚀 Key Features

- **Automated Testing**: Multi-OS, multi-Python version testing matrix
- **Semantic Versioning**: Automatic version bumps based on commit messages
- **Code Quality**: Linting, formatting, type checking, and security scanning
- **Coverage Reporting**: Detailed test coverage with Codecov integration
- **Automated Releases**: PyPI publishing and GitHub release creation
- **Pre-commit Hooks**: Local quality checks before commits

## 📋 CI/CD Components

### 1. Continuous Integration (CI)

#### Test Matrix
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Ubuntu, Windows, macOS
- **Test Types**: Unit, Integration, System

#### Quality Gates
- ✅ Linting with Ruff
- ✅ Formatting with Black
- ✅ Type checking with mypy
- ✅ Security scanning with Bandit
- ✅ Dependency scanning with Safety
- ✅ Test coverage > 80% (goal)

### 2. Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

#### Commit Message Convention

```
type(scope): subject

body

footer
```

**Types that trigger releases:**
- `feat`: New feature (MINOR)
- `fix`: Bug fix (PATCH)
- `perf`: Performance improvement (PATCH)
- `BREAKING CHANGE`: Breaking change (MAJOR)

**Other types (no release):**
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### 3. Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

Hooks include:
- Trailing whitespace removal
- End-of-file fixing
- YAML/TOML validation
- Large file prevention
- Python code formatting (Black)
- Python linting (Ruff)
- Type checking (mypy)
- Security scanning (Bandit)
- Commit message validation (Commitizen)

Run manually:
```bash
pre-commit run --all-files
```

### 4. GitHub Actions Workflows

#### CI Pipeline (`ci.yml`)
Triggered on:
- Push to main/develop branches
- Pull requests
- Manual dispatch

Features:
- Concurrent job management
- Path-based triggering (ignores docs)
- Multi-OS testing
- Coverage reporting
- Security scanning
- Build verification

#### Release Pipeline (`release.yml`)
Triggered on:
- Push to main branch (automatic)
- Manual dispatch (forced release)

Features:
- Automatic version detection
- Changelog generation
- PyPI publishing
- GitHub release creation
- Test PyPI publishing (staging)

## 🔧 Setup Instructions

### 1. Local Development Setup

```bash
# Clone repository
git clone https://github.com/rfd-protocol/rfd.git
cd rfd

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Run tests
pytest

# Run linting
ruff check src tests
black --check src tests
```

### 2. Making Changes

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# ... edit files ...

# Run pre-commit checks
pre-commit run --all-files

# Run tests
pytest

# Commit with conventional message
git commit -m "feat: add new validation method"

# Push and create PR
git push origin feature/your-feature
```

### 3. Release Process

Releases are automated based on commit messages:

1. **Automatic Release** (Recommended)
   ```bash
   # Commit with release-triggering message
   git commit -m "feat: major new feature"
   git push origin main
   # CI automatically creates release
   ```

2. **Manual Release** (If needed)
   - Go to Actions → Release Pipeline
   - Click "Run workflow"
   - Select release type (patch/minor/major)
   - Run workflow

### 4. PyPI Token Setup

For maintainers to enable PyPI publishing:

1. Create PyPI API token at https://pypi.org/manage/account/token/
2. Add as GitHub secret: `PYPI_API_TOKEN`
3. Create Test PyPI token (optional): `TEST_PYPI_API_TOKEN`

## 📊 Monitoring

### Test Coverage
- Target: 80% coverage
- Current: ~32% (improving during dogfooding)
- Reports: Available in GitHub Actions artifacts
- Codecov: Integration ready (token optional)

### Security Scanning
- **Bandit**: AST-based security linter
- **Safety**: Dependency vulnerability scanner
- Reports uploaded as artifacts

### Performance Metrics
- CI runtime: ~5-10 minutes
- Test execution: ~30 seconds
- Build time: ~20 seconds

## 🐛 Troubleshooting

### Common Issues

1. **Pre-commit failures**
   ```bash
   # Auto-fix formatting issues
   black src tests
   ruff check --fix src tests
   ```

2. **Test failures**
   ```bash
   # Run specific test
   pytest tests/test_components.py::TestValidationEngine -xvs
   
   # Run with debugging
   pytest --pdb --maxfail=1
   ```

3. **Release not triggered**
   - Check commit message format
   - Ensure pushing to main branch
   - Check GitHub Actions logs

## 🔗 Resources

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Documentation](https://pre-commit.com/)

## 📝 Maintenance

### Weekly Tasks
- Review and merge dependabot updates
- Check security scan results
- Monitor test coverage trends

### Monthly Tasks
- Review and update dependencies
- Analyze CI/CD performance metrics
- Update documentation as needed

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped correctly
- [ ] PyPI package published
- [ ] GitHub release created
- [ ] Announcement made (if major release)

---

*Last updated: 2024*
*Version: 1.0.0*