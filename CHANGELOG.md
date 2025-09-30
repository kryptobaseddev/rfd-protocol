# CHANGELOG

<!-- version list -->

## v5.5.0 (2025-09-30)

### Features

- Implement complete prevention system v5.3.1
  ([`919324c`](https://github.com/kryptobaseddev/rfd-protocol/commit/919324c1644b5f58532c1abfeb1177153b11bec2))

### Bug Fixes

- Complete prevention system implementation with all features working
  - Added `_save_validation_to_db()` method for stats persistence
  - Fixed CLI validate command to read from files before stdin
  - Implemented complete `WorkflowLockManager` class with CLI commands
  - Fixed scope boundaries logic for proper directory/file checking
  - Extended allowed files list (CLAUDE.md, LICENSE, etc.)
  - Fixed git diff to exclude deleted files (--diff-filter=ACMRUXB)
  - All 5 prevention features now pass comprehensive tests (100% pass rate)

### Documentation

- Added VERSION_MANAGEMENT.md with strict versioning rules
- Updated AGENTS.md with proper RFD workflow instructions

### Chores

- Synced versions to PyPI latest (5.5.0) to fix version mismatch
- Added git pre-commit hook to prevent manual version changes
- Increased max_files limit to 75 for growing codebase

## v5.4.0 (2025-09-26)

### Chores

- Bump version to 5.3.1 (patch release)
  ([`9c3c963`](https://github.com/kryptobaseddev/rfd-protocol/commit/9c3c963240371bc3dee0a5bcea34fdcd67b2a02c))

### Features

- Implement automated QA cycles feature (v5.3.1)
  ([`c6fe377`](https://github.com/kryptobaseddev/rfd-protocol/commit/c6fe3770f697876d36dc46c0ea869bfbe848bb7b))


## v5.3.0 (2025-09-26)

### Bug Fixes

- Add validate-commit command for pre-commit hook
  ([`96b3c0e`](https://github.com/kryptobaseddev/rfd-protocol/commit/96b3c0e7005e20df14f09c3df2de6ae5225441e3))

### Features

- Add gap-aware resume and template sync checking
  ([`ed346e8`](https://github.com/kryptobaseddev/rfd-protocol/commit/ed346e89b3e6d231c90c8315d6b0979506419f29))

- Implement partial enforcement features for v5.2.0
  ([`4589ab5`](https://github.com/kryptobaseddev/rfd-protocol/commit/4589ab5c0c4ebe946e9489ed320e4745bc138d91))


## v5.2.0 (2025-09-26)

### Features

- Enhanced session management with optional git worktree isolation
  ([`9a2c97c`](https://github.com/kryptobaseddev/rfd-protocol/commit/9a2c97c41e648402cb564524ef232acadf1362ed))


## v5.1.1 (2025-09-26)

### Bug Fixes

- Update __version__ and fix constitution database schema
  ([`00ce981`](https://github.com/kryptobaseddev/rfd-protocol/commit/00ce981092ec6c99fe64ccd373bbb886d37621a9))


## v5.1.0 (2025-09-25)

### Features

- **true-database-first**: Complete removal of file-based progress tracking
  - Removed all PROGRESS.md generation and references
  - Constitution now stored in database, not files
  - All specs and memory directories moved under `.rfd/`
  - Single database (`memory.db`) - removed redundant `rfd.db`

### Bug Fixes

- **schema-consistency**: Fixed database schema inconsistencies
  - Standardized `features` table schema across all modules
  - Fixed `sessions` table to use consistent columns
  - Fixed `checkpoints` table to include evidence column
  - Updated tests to reflect database-first approach

- **hallucination-prevention**: Added "No Hallucination" principle to constitution
  - AI claims must be validated
  - No lying about completions
  - Addresses core issues from brain-dump.md

### Improvements

- **file-organization**: Proper encapsulation in `.rfd/` directory
  - No project-specific files outside `.rfd/`
  - Cleaner project root
  - Better separation of concerns

## v5.0.0 (2025-09-25)

### Breaking Changes

- **database-first**: Complete migration to database-first architecture
  - PROJECT.md and PROGRESS.md are now deprecated
  - All project configuration now in `.rfd/config.yaml`
  - Features are managed exclusively in the database
  - Context files are auto-generated and protected from manual editing

### Features

- **context-manager**: Add ContextManager for programmatic context handling
  - Auto-generates `.rfd/context/` files with DO NOT EDIT warnings
  - Prevents AI/LLM agents from manually editing context files
  - Provides safe read-only access for AI agents
  ([`current`](https://github.com/kryptobaseddev/rfd-protocol/commit/current))

- **database-accountability**: Add `rfd audit` command for database-first compliance
  - Detects status mismatches between files and database
  - Identifies orphaned sessions and missing task tracking
  - Provides specific fixes for each violation
  ([`current`](https://github.com/kryptobaseddev/rfd-protocol/commit/current))

- **session-commands**: Add missing session management commands
  - `rfd session status` - Shows current session details
  - `rfd session current` - Alias for status command
  - Both commands query database for authoritative feature status
  ([`current`](https://github.com/kryptobaseddev/rfd-protocol/commit/current))

### Fixes

- **validation**: Fix validation to use database status instead of PROJECT.md
- **session**: Remove all PROJECT.md dependencies from session management
- **spec**: Update load_project_spec() to use database and config.yaml

### Documentation

- Update CLAUDE.md to forbid editing auto-generated context files
- Add .gitattributes to mark context files as linguist-generated
- Update all command templates to reference config.yaml instead of PROJECT.md

## v4.2.1 (2025-09-25)

### Bug Fixes

- Add missing packaging dependency for version checks
  ([`a2b9b29`](https://github.com/kryptobaseddev/rfd-protocol/commit/a2b9b2924e64df5a1a9bc00d91a29492d4221cdf))

## v4.2.0 (2025-09-25)

### Features

- **commands**: Improve slash commands with better parameter hints and discovery
  ([`192ac2e`](https://github.com/kryptobaseddev/rfd-protocol/commit/192ac2ec6832c212b34d67a06b3e2bb83b055103))


## v4.1.0 (2025-09-24)

### Documentation

- Improve README with clearer problem statement and better structure
  ([`f9f0418`](https://github.com/kryptobaseddev/rfd-protocol/commit/f9f041830e72ebed9763f4509cf94656d3e5df6c))

### Features

- Major CLI refactor v4.1.0 - cleaner command structure
  ([`156e3bc`](https://github.com/kryptobaseddev/rfd-protocol/commit/156e3bcb716f12aebcf6f84af4b13163c279f4bd))


## v4.0.0 (2025-09-24)

### Features

- Major v2.4.0 release with spec-kit parity and WAL mode
  ([`b360f57`](https://github.com/kryptobaseddev/rfd-protocol/commit/b360f57c787457e01e9ab13e91bdab4572f7ec4e))

### Breaking Changes

- Database now uses WAL mode for better concurrency


## v3.0.0 (2025-09-24)

### Chores

- Bump version to 2.4.0 for release
  ([`c0b36bd`](https://github.com/kryptobaseddev/rfd-protocol/commit/c0b36bde54c67e745eb4a6b3c1435c3c42cd3cda))

### Documentation

- Comprehensive documentation suite for RFD v2.1.0
  ([`430521f`](https://github.com/kryptobaseddev/rfd-protocol/commit/430521fa5e4edfdd5b3ca1c8eb79a1b5af6255c0))

### Features

- Major enhancements - WAL mode, /rfd-analyze command, comprehensive docs
  ([`2f06f4d`](https://github.com/kryptobaseddev/rfd-protocol/commit/2f06f4debd96609bcaed34dcbd830ba5898f8c46))

- Major RFD improvements - migration system, auto-handoff, and proper architecture
  ([`0edaac7`](https://github.com/kryptobaseddev/rfd-protocol/commit/0edaac76dd7fe92c0da919c2ecbbf79a6c0c327c))


## v2.2.0 (2025-09-23)

### Chores

- Adjust line limit to accommodate spec generator
  ([`949b49b`](https://github.com/kryptobaseddev/rfd-protocol/commit/949b49b8bc11658f7b60f9f8c95cdadd2a81d01f))

### Features

- Comprehensive spec generation and enhanced initialization for v2.0.3
  ([`2f27505`](https://github.com/kryptobaseddev/rfd-protocol/commit/2f275059144e21e873b81b3fae54e4245b8578ef))


## v2.1.0 (2025-09-23)

### Features

- Major RFD improvements for true dogfooding
  ([`703b01e`](https://github.com/kryptobaseddev/rfd-protocol/commit/703b01ec4630afed8995b6961bdd756a4d897c22))


## v2.0.2 (2025-09-23)

### Bug Fixes

- Test semantic release trigger for v2.0.2
  ([`fb7aa41`](https://github.com/kryptobaseddev/rfd-protocol/commit/fb7aa417deee55e1b045e4de001bf6e213fd2c70))

### Chores

- Clean up duplicate files and update original plan
  ([`d67ed91`](https://github.com/kryptobaseddev/rfd-protocol/commit/d67ed91fd1667e85c9c7cd6b30fbf1cb0f6f7bda))

- Organize documentation and preserve RFD system files
  ([`4985863`](https://github.com/kryptobaseddev/rfd-protocol/commit/4985863b53e78dfe29f45a0ce204b5add959721b))

### Documentation

- Complete session handoff and plan consolidation
  ([`0ec4101`](https://github.com/kryptobaseddev/rfd-protocol/commit/0ec4101ab1489f554f0b66ccb70e38749ef56867))

- Ready for PyPI publishing summary
  ([`0e660ae`](https://github.com/kryptobaseddev/rfd-protocol/commit/0e660ae6b4db713b9afe7e546ff3b99b7ab000d6))

- Updated session plan for PyPI publishing and dogfooding
  ([`dc557c7`](https://github.com/kryptobaseddev/rfd-protocol/commit/dc557c740fd04f9b648b92012bcb62b56d09066f))


## v2.0.1 (2025-09-23)

### Bug Fixes

- Add --version flag support to CLI
  ([`59670d7`](https://github.com/kryptobaseddev/rfd-protocol/commit/59670d7d6a1476c0bf057e904a8fde761ae2ad4a))


## v2.0.0 (2025-09-23)

### Bug Fixes

- CI/CD pipeline and semantic versioning setup
  ([`306559b`](https://github.com/kryptobaseddev/rfd-protocol/commit/306559bca5653e579b98460c88c81a595d431899))

- SessionManager create_session test now passing
  ([`125f862`](https://github.com/kryptobaseddev/rfd-protocol/commit/125f862ac5131cad90fe82ccb8615c066c919da9))

- SessionManager tests and database setup
  ([`3f9908d`](https://github.com/kryptobaseddev/rfd-protocol/commit/3f9908d8e7931669eb0035b047d01bb7d7d2cbcd))

- SpecEngine tests and add missing API methods
  ([`a8dd479`](https://github.com/kryptobaseddev/rfd-protocol/commit/a8dd4791a06f391262f19a0835b916b927fa97ac))

- **ci**: Fix CI/CD pipeline issues and improve robustness
  ([`b11a5a3`](https://github.com/kryptobaseddev/rfd-protocol/commit/b11a5a30a3b068462df29115010bd155800b2f97))

### Chores

- Clean up coverage artifacts
  ([`ab363e5`](https://github.com/kryptobaseddev/rfd-protocol/commit/ab363e5c240ed6f38069235f8ce5e8c8e4520cc8))

- Update progress tracking and memory database
  ([`8c1f11d`](https://github.com/kryptobaseddev/rfd-protocol/commit/8c1f11db35f6b1b7174ed38fb6427b1e103d8ab8))

### Documentation

- Add comprehensive session summary
  ([`eaa0034`](https://github.com/kryptobaseddev/rfd-protocol/commit/eaa003421ef3ab3255a6f46d99d9aba093ae8871))

- Complete session handoff with comprehensive documentation
  ([`27c9e5e`](https://github.com/kryptobaseddev/rfd-protocol/commit/27c9e5e99208a46965c4d60f7b5e757a33df40f6))

- Comprehensive CI/CD improvements summary
  ([`6e3e497`](https://github.com/kryptobaseddev/rfd-protocol/commit/6e3e4974634c15b015f79c49e53010bc64717810))

- Comprehensive next session plan for pipeline validation
  ([`37e31c1`](https://github.com/kryptobaseddev/rfd-protocol/commit/37e31c1830303c9dedc0ac5f914cea8dbf9d6e19))

- Session complete - ready for pipeline validation
  ([`abb21c8`](https://github.com/kryptobaseddev/rfd-protocol/commit/abb21c8047502039aca91216f461beeeb3711384))

### Features

- Production-ready CI/CD pipelines
  ([`0853a6b`](https://github.com/kryptobaseddev/rfd-protocol/commit/0853a6b7ef2a8816022404018172fcfde3c5c98d))

### Breaking Changes

- Requires PYPI_API_TOKEN and TEST_PYPI_API_TOKEN secrets for publishing


## v1.0.0 (2025-09-22)

- Initial Release
