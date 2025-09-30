# Version Management Rules - CRITICAL

## ⚠️ NEVER MANUALLY CHANGE VERSIONS

The RFD Protocol uses **python-semantic-release** for ALL version management.

## The Single Source of Truth

**GitHub Actions + semantic-release** control versions automatically based on commit messages:

### Commit Prefixes → Version Bumps:
- `feat:` → Minor version (5.2.0 → 5.3.0)
- `fix:` → Patch version (5.2.0 → 5.2.1)  
- `perf:` → Patch version (5.2.0 → 5.2.1)
- `BREAKING CHANGE:` in body → Major version (5.2.0 → 6.0.0)
- `chore:`, `docs:`, `style:`, `refactor:`, `test:` → NO VERSION CHANGE

### Files That Auto-Update:
1. `pyproject.toml` - `version = "X.X.X"`
2. `src/rfd/__init__.py` - `__version__ = "X.X.X"`
3. `.rfd/.template_version` - (manually sync if needed)

## ❌ FORBIDDEN Actions:

1. **NEVER manually edit version in:**
   - `pyproject.toml`
   - `src/rfd/__init__.py`
   - Any other file

2. **NEVER commit with:**
   - `chore: bump version to X.X.X`
   - `chore: update version`
   - Any manual version change

3. **NEVER run:**
   - `python -m build && twine upload` (let GitHub Actions do it)
   - `git tag vX.X.X` (semantic-release creates tags)

## ✅ CORRECT Workflow:

1. **Make your changes**
2. **Commit with proper prefix**:
   ```bash
   git commit -m "feat: add new prevention system"
   git commit -m "fix: resolve scope boundary bug"
   ```
3. **Push to main**:
   ```bash
   git push origin main
   ```
4. **GitHub Actions automatically**:
   - Detects commit type
   - Calculates version bump
   - Updates version files
   - Creates git tag
   - Publishes to PyPI
   - Creates GitHub release

## 📊 Current State (as of this fix):

- **PyPI Latest**: 5.5.0
- **Git Tag Latest**: v5.2.0 (out of sync!)
- **Local Files**: 5.6.0 (manually set, wrong!)

## 🔧 How to Fix Current Mess:

1. Set all versions to match PyPI (5.5.0)
2. Commit with `fix:` prefix for patch bump to 5.5.1
3. Let GitHub Actions handle everything
4. NEVER touch versions manually again

## 🚨 If Versions Get Out of Sync:

1. **Check PyPI**: `pip index versions rfd-protocol`
2. **Check git tags**: `git tag --sort=-version:refname`
3. **Check current**: `cat pyproject.toml | grep version`
4. **Sync to PyPI version** (highest published)
5. **Use only semantic commits** going forward

## Example Commit Messages:

### Will bump version:
```bash
git commit -m "feat: implement workflow locks"
git commit -m "fix: database persistence bug"
git commit -m "perf: optimize validation speed"
```

### Won't bump version:
```bash
git commit -m "docs: update README"
git commit -m "chore: clean up imports"
git commit -m "test: add unit tests"
```

## Remember:
**The pipeline owns versioning. You own features. Stay in your lane!**