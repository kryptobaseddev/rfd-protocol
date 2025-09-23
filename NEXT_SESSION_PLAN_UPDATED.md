# Next Session Plan - PyPI Publishing & Dogfooding Validation

## ✅ Already Completed
- **Version**: Now at 2.0.0 (semantic versioning is working!)
- **Tests**: SessionManager (6/6), SpecEngine (4/5) passing
- **CI/CD**: All pipelines configured and passing
- **Database**: SQLite setup complete
- **PyPI Secrets**: ✅ ADDED (Thank you!)
- **--version flag**: ✅ FIXED

## 🎯 Primary Goals for Next Session

### 1. Publish to Test PyPI First
```bash
# Clean previous builds
rm -rf dist/ build/

# Build fresh package
python -m build

# Check package integrity
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install -i https://test.pypi.org/simple/ rfd-protocol==2.0.0

# Verify it works
rfd --version  # Should show 2.0.0
rfd --help
```

### 2. Publish to Production PyPI
```bash
# Once Test PyPI works, publish to production
twine upload dist/*

# Install from production PyPI
pip uninstall rfd-protocol -y
pip install rfd-protocol

# Verify installation
rfd --version
```

### 3. 🐕 Dogfooding Test - Critical Validation

This is the most important test - using RFD to manage RFD itself:

```bash
# Create a test directory
mkdir ~/rfd-dogfood-test
cd ~/rfd-dogfood-test

# Install RFD from PyPI
pip install rfd-protocol

# Initialize RFD in the project
rfd init

# Create a spec for a new feature
rfd spec create

# Example feature to add:
# - Feature: "Add JSON export for validation reports"
# - Description: "Export validation results as JSON for CI integration"

# Run the full workflow
rfd check
rfd validate
rfd build
rfd checkpoint "Dogfooding test successful"

# Try to fix any validation errors using RFD itself
```

### 4. Full Dogfooding on RFD Repository

```bash
# Clone the actual RFD repository
git clone https://github.com/kryptobaseddev/rfd-protocol rfd-dogfood
cd rfd-dogfood

# Use installed RFD to manage the project
rfd check
rfd validate

# Fix any validation errors
# The main issues are:
# - Too many files (48 > 30 max)
# - Files too long (several > 500 lines)

# Use RFD to track fixing these issues
rfd checkpoint "Starting file consolidation"
```

## 📋 Validation Checklist

### Package Publishing
- [ ] Package builds without errors
- [ ] Twine check passes
- [ ] Test PyPI upload successful
- [ ] Test PyPI installation works
- [ ] Production PyPI upload successful
- [ ] Production PyPI installation works
- [ ] `rfd --version` shows 2.0.0

### Dogfooding Tests
- [ ] RFD can initialize in empty directory
- [ ] RFD can create PROJECT.md
- [ ] RFD validates its own structure
- [ ] RFD can track checkpoints
- [ ] RFD can manage the RFD repository itself

### Integration Tests
- [ ] Works with Python 3.8-3.12
- [ ] SQLite database creates properly
- [ ] All CLI commands function
- [ ] Session persistence works

## 🔧 Fixing Current Validation Issues

The project currently fails validation due to:
1. **Too many files** (48 files, max 30)
2. **Files too long** (9 files over 500 lines)

### Strategy to Fix:
1. Consolidate test files
2. Split large source files into smaller modules
3. Remove unnecessary files
4. Use RFD to track this refactoring

## 📊 Success Metrics

The session is successful when:
1. ✅ RFD is published on PyPI
2. ✅ Anyone can `pip install rfd-protocol`
3. ✅ RFD can manage its own development
4. ✅ Validation passes (or we have a plan to fix)
5. ✅ Documentation is updated with PyPI badge

## 🚀 Quick Start Commands for Next Session

```bash
# 1. Start here
cd /mnt/projects/rfd-protocol
git pull origin main

# 2. Build and publish
python -m build
twine upload --repository testpypi dist/*

# 3. Test installation
pip install -i https://test.pypi.org/simple/ rfd-protocol==2.0.0

# 4. Dogfood test
mkdir ~/rfd-test && cd ~/rfd-test
rfd init
rfd check
rfd validate

# 5. If all good, publish to production
cd /mnt/projects/rfd-protocol
twine upload dist/*
```

## 🎉 End Goal

By the end of the session:
- **RFD Protocol is on PyPI** - Anyone can install it
- **Dogfooding proven** - RFD manages itself
- **Ready for community** - Public announcement ready
- **Version 2.0.0 live** - Semantic versioning working

## Notes

- PyPI package name: `rfd-protocol`
- Current version: 2.0.0
- GitHub: https://github.com/kryptobaseddev/rfd-protocol
- PyPI page (once published): https://pypi.org/project/rfd-protocol/

The main focus is **proving RFD can manage its own development** - this is the ultimate validation that the tool works!