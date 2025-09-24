# RFD Release Process

## Current Situation
- **Local Development**: v2.2.0 (in src/rfd/)
- **PyPI Published**: v2.0.2 
- **Uncommitted Changes**: Many improvements

## Release Steps

### 1. Test Locally
```bash
# Test with development version
./rfd validate
./rfd build
pytest

# Test as installed package
pip install -e .
cd /tmp/test-project
rfd init
rfd session start test
```

### 2. Commit Changes
```bash
# Review changes
git status
git diff

# Commit with conventional commits (for semantic release)
git add .
git commit -m "feat: add migration system and proper update workflow"
```

### 3. Push to GitHub
```bash
git push origin main
```

### 4. CI/CD Will:
- Run tests
- Use semantic-release to determine version
- Update version in pyproject.toml and src/rfd/__init__.py
- Create GitHub release
- Publish to PyPI

### 5. Users Update
```bash
# Users get new version
pip install --upgrade rfd-protocol

# Migrate projects if needed
cd their-project/
rfd migrate
```

## Version Management

### Automatic (via CI/CD):
- `python-semantic-release` reads commit messages
- Updates version in:
  - `pyproject.toml`
  - `src/rfd/__init__.py`
- Creates git tag
- Publishes to PyPI

### Manual (for development):
```bash
# Bump version manually if needed
# Edit pyproject.toml and src/rfd/__init__.py
```

## Testing Before Release

### As Developer:
```bash
# Use development version
./rfd status
./rfd validate
```

### As User Would:
```bash
# Install in test environment
python -m venv test-env
source test-env/bin/activate
pip install -e .

# Test in new project
cd /tmp
mkdir test-project
cd test-project
rfd init
```

## Are We Ready to Release?

### Checklist:
- [ ] All tests pass locally
- [ ] Development version (./rfd) works
- [ ] Can install with pip install -e .
- [ ] rfd init creates projects correctly
- [ ] Migration system works
- [ ] Claude commands copy correctly

### Known Issues:
- Need to commit and push changes
- Need to test full workflow
- Version tracking in .rfd/ needs testing