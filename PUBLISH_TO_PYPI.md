# Publishing RFD to PyPI

## Version 2.4.0 Ready for Release

The distribution packages have been built and are ready in the `dist/` directory:
- `rfd_protocol-2.4.0.tar.gz`
- `rfd_protocol-2.4.0-py3-none-any.whl`

## To Publish to PyPI

Run the following command with your PyPI credentials:

```bash
twine upload dist/rfd_protocol-2.4.0*
```

You'll need:
- PyPI username or `__token__` for API token auth
- PyPI password or API token

## What's New in 2.4.0

### Major Enhancements
- **SQLite WAL Mode**: Better concurrency and crash recovery
- **Cross-Artifact Analysis**: New `/rfd-analyze` command for consistency checking
- **Spec-Kit Feature Parity**: All spec-kit commands now available
- **Comprehensive Documentation**: Complete RFD Walkthrough added

### Improvements
- Removed all model/temperature/token references from commands
- Fixed database foreign key handling
- Enhanced memory persistence across sessions
- Updated README with clear, factual instructions

### Verified Functionality
- All brain-dump.md concerns addressed
- Installation from PyPI tested and working
- All commands verified functional
- Documentation accuracy confirmed

## Post-Publishing Steps

1. Verify on PyPI: https://pypi.org/project/rfd-protocol/
2. Test installation: `pip install --upgrade rfd-protocol`
3. Update GitHub release notes
4. Announce on social channels if applicable