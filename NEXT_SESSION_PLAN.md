# Next Session Plan - Pipeline Validation & PyPI Publishing

## Current State
- **Version**: 2.0.1 (semantic versioning working!)
- **Tests**: SessionManager (6/6), SpecEngine (4/5) passing
- **CI/CD**: All pipelines passing ✅
- **Database**: SQLite setup complete
- **PyPI Secrets**: Added ✅
- **Commits**: All pushed and up to date

## Immediate Tasks for Next Session

### 1. ✅ COMPLETED - Pipelines Running
- All changes pushed
- CI/CD pipelines passing
- Semantic versioning working (bumped to 2.0.1)

### 2. ✅ COMPLETED - GitHub Secrets Added
- `PYPI_API_TOKEN` - Added ✅
- `TEST_PYPI_API_TOKEN` - Added ✅
- Ready for PyPI publishing!

### 3. Validate CI Pipeline
```bash
# Check GitHub Actions
# https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/ci.yml

# Expected outcomes:
# ✅ Tests run on all Python versions
# ✅ Linting passes or continues on error
# ✅ Coverage reports generated
```

### 4. Test Semantic Release
```bash
# Make a test commit with conventional format
echo "# Test" >> test.md
git add test.md
git commit -m "fix: test semantic release trigger"
git push origin main

# Version already bumped to 2.0.1 automatically!
```

### 5. Manual PyPI Publishing Test
```bash
# Build the package locally
python -m build

# Test upload to Test PyPI (requires TEST_PYPI_API_TOKEN)
twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install -i https://test.pypi.org/simple/ rfd-protocol==2.0.1
```

### 6. Production PyPI Release
Once Test PyPI works:
```bash
# Upload to production PyPI (requires PYPI_API_TOKEN)
twine upload dist/*

# Install from PyPI
pip install rfd-protocol

# Verify installation
rfd --version
```

### 7. Dogfooding Test - Use RFD on Itself
```bash
# Clone fresh copy
git clone https://github.com/kryptobaseddev/rfd-protocol rfd-test
cd rfd-test

# Install RFD from PyPI
pip install rfd-protocol

# Use RFD to manage its own development
rfd init
rfd spec create
rfd build
rfd validate

# This proves the tool works on itself!
```

## Success Criteria

### ✅ Pipeline Validation Complete When:
1. CI Pipeline runs without fatal errors
2. Release Pipeline triggers on semantic commits
3. Package builds successfully
4. Test PyPI upload works
5. Production PyPI upload works
6. Package installable via `pip install rfd-protocol`
7. RFD can manage its own development (dogfooding)

## Troubleshooting Guide

### If CI Pipeline Fails:
- Check Python version compatibility
- Review test failures in Actions logs
- Verify dependencies install correctly

### If Release Pipeline Fails:
- Confirm semantic-release configuration
- Check commit message format
- Verify version files are in sync

### If PyPI Upload Fails:
- Verify tokens are set correctly
- Check package name availability
- Review twine check output
- Ensure version doesn't already exist

### If Dogfooding Fails:
- Check RFD installation path
- Verify database initialization
- Review PROJECT.md structure
- Check file permissions

## Commands Reference

```bash
# Check current version
cat pyproject.toml | grep version

# Run tests locally
pytest tests/ -v

# Build package
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to Production PyPI
twine upload dist/*

# Install from PyPI
pip install rfd-protocol

# Verify RFD works
rfd --version
rfd --help
```

## Notes for Repository Owner

⚠️ **CRITICAL**: You MUST add the PyPI tokens as GitHub secrets before the release pipeline can work:
- `PYPI_API_TOKEN` - Required for production releases
- `TEST_PYPI_API_TOKEN` - Required for test releases

Without these, the pipelines will run but publishing will fail.

## Expected Timeline

1. Push to remote: 2 minutes
2. CI Pipeline run: 5-10 minutes  
3. Add secrets: 5 minutes (owner action)
4. Test semantic release: 5 minutes
5. Test PyPI publish: 10 minutes
6. Production PyPI publish: 5 minutes
7. Dogfooding validation: 15 minutes

**Total: ~45-60 minutes**

## End Goal

By the end of the next session, RFD Protocol should be:
- ✅ Fully tested via CI/CD
- ✅ Published on PyPI
- ✅ Installable via pip
- ✅ Self-hosting (using RFD to develop RFD)
- ✅ Ready for production use