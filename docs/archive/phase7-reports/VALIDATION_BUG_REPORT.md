# ValidationEngine File Pattern Bug Report

## Critical Issue Found During Testing
**Date**: 2025-09-21
**Discovered by**: RFD-2 (Test Suite Developer)

## Problem
The ValidationEngine in `.rfd/validation.py` has a CRITICAL bug that prevents it from being truly tech-stack agnostic. The `_extract_file_claims()` method only recognizes a limited set of file extensions.

## Current Limitations
The patterns in lines 287-292 only detect these extensions:
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx`
- Documentation: `.md`, `.txt`
- Config: `.json`, `.yaml`, `.yml`

## Missing Support
The following common file types are NOT detected:
- **Java**: `.java`, `.class`, `.jar`
- **C/C++**: `.c`, `.cpp`, `.cc`, `.h`, `.hpp`
- **C#**: `.cs`, `.csproj`
- **Go**: `.go`, `.mod`
- **Rust**: `.rs`, `.toml`
- **Ruby**: `.rb`, `.erb`
- **PHP**: `.php`
- **Swift**: `.swift`
- **Kotlin**: `.kt`
- **Shell**: `.sh`, `.bash`, `.zsh`
- **Web**: `.html`, `.htm`, `.css`, `.scss`, `.sass`
- **Config**: `.xml`, `.ini`, `.conf`, `.env`
- **Build**: `Makefile`, `Dockerfile`, `.dockerfile`
- **Database**: `.sql`
- **Data**: `.csv`, `.tsv`

## Impact
This bug means RFD **CANNOT** work as a drop-in tool for:
- Java projects
- C/C++ projects
- Go projects
- Rust projects
- Ruby projects
- Mobile apps (Swift/Kotlin)
- Many other tech stacks

## Test Failures
The following tests fail due to this bug:
- `test_validation_engine_tech_agnostic` (Main.java not detected)
- `test_validation_detects_any_file_type` (multiple extensions fail)
- `test_validation_handles_nested_paths` (non-Python files fail)

## Recommended Fix
Replace the hardcoded extension list with a more comprehensive pattern or remove extension filtering entirely:

```python
def _extract_file_claims(self, text: str) -> List[str]:
    """Extract file paths mentioned in AI claims"""
    patterns = [
        # Match any file with an extension
        r'[cC]reated?\s+(?:file\s+)?([^\s]+\.[a-zA-Z0-9]+)',
        r'[wW]rote?\s+(?:to\s+)?([^\s]+\.[a-zA-Z0-9]+)',
        r'[fF]ile\s+([^\s]+\.[a-zA-Z0-9]+)',
        r'`([^\s`]+\.[a-zA-Z0-9]+)`',
        r'"([^\s"]+\.[a-zA-Z0-9]+)"',
        r'\'([^\s\']+\.[a-zA-Z0-9]+)\'',
        # Also match common files without extensions
        r'[cC]reated?\s+(Makefile|Dockerfile|Gemfile|Rakefile|Procfile)',
    ]
```

## Additional Bug: Regex Matching Issue
The regex pattern `(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml)` has a matching bug where:
- "config.json" incorrectly extracts as "config.js" (matches 'js' inside 'json')
- This causes false negatives even for supported file types

## Severity
**CRITICAL** - These bugs prevent RFD from achieving its core promise of being a universal, drop-in development tool.

## Workaround for Tests
Tests have been updated to only test with supported file extensions until the core bug is fixed.