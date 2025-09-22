# GitHub Actions Secrets Setup

This document describes the secrets required for the CI/CD pipelines to work properly.

## Required Secrets

### For PyPI Publishing

1. **PYPI_API_TOKEN**
   - Generate at: https://pypi.org/manage/account/token/
   - Used for publishing releases to PyPI
   - Required for production releases

2. **TEST_PYPI_API_TOKEN**
   - Generate at: https://test.pypi.org/manage/account/token/
   - Used for testing package publishing
   - Optional but recommended

### For GitHub Release Automation

The workflow uses the default `GITHUB_TOKEN` which is automatically provided.

## Setting up Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with the exact names listed above

## Testing the Pipeline

After setting up secrets:

1. Create a test branch with conventional commits
2. Open a PR to trigger the CI pipeline
3. Merge to main to trigger the release pipeline

## Troubleshooting

- If PyPI publishing fails, check that tokens are valid and not expired
- Ensure package name is available on PyPI
- Check that version numbers are correctly incremented