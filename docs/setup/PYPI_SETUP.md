# PyPI Publishing Setup Guide

## Required GitHub Secrets

You need to add these secrets to your GitHub repository for automated PyPI publishing:

### 1. PYPI_API_TOKEN (Required)
This is for publishing to the official PyPI repository.

**Steps to create:**
1. Go to https://pypi.org/manage/account/
2. Log in or create an account
3. Navigate to "Account settings" → "API tokens"
4. Click "Add API token"
5. Name: "GitHub Actions - rfd-protocol"
6. Scope: "Project: rfd-protocol" (or "Entire account" if project doesn't exist yet)
7. Copy the token (starts with `pypi-`)

**Add to GitHub:**
1. Go to https://github.com/kryptobaseddev/rfd-protocol/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste the token from PyPI
5. Click "Add secret"

### 2. TEST_PYPI_API_TOKEN (Optional but Recommended)
This is for testing releases on Test PyPI before publishing to production.

**Steps to create:**
1. Go to https://test.pypi.org/manage/account/
2. Create an account if you don't have one (separate from pypi.org)
3. Navigate to "Account settings" → "API tokens"
4. Click "Add API token"
5. Name: "GitHub Actions - rfd-protocol"
6. Scope: "Entire account"
7. Copy the token (starts with `pypi-`)

**Add to GitHub:**
1. Go to https://github.com/kryptobaseddev/rfd-protocol/settings/secrets/actions
2. Click "New repository secret"
3. Name: `TEST_PYPI_API_TOKEN`
4. Value: Paste the token from Test PyPI
5. Click "Add secret"

## Important Notes

- **NOT GITHUB_TOKEN**: The `GITHUB_TOKEN` mentioned in workflows is automatically provided by GitHub Actions. You do NOT need to create this.
- **Token Security**: Never commit these tokens to the repository or share them publicly
- **Token Expiration**: PyPI tokens don't expire by default, but you can revoke them anytime
- **Token Permissions**: Use project-specific tokens when possible for better security

## Testing the Setup

After adding the secrets, you can test the release pipeline:

1. Make a commit with conventional commit message (e.g., `fix: some bug`)
2. Push to main branch
3. Check Actions tab to see if the release workflow runs
4. For manual testing: Go to Actions → Release Pipeline → Run workflow

## Troubleshooting

### If publishing fails:
- Check that the package name `rfd-protocol` is available on PyPI
- Verify the tokens are correctly set in GitHub Secrets
- Ensure tokens have the correct permissions
- Check the Actions logs for specific error messages

### Common Issues:
- **403 Forbidden**: Token is invalid or doesn't have permission
- **400 Bad Request**: Package metadata is invalid
- **409 Conflict**: Version already exists on PyPI