# Project Constitution
Generated: 2025-09-24T12:41:26.341157

## Core Principles
These principles are IMMUTABLE and guide all development decisions.

### 1. Reality First
- Code must run and pass tests before considered complete
- No mock data in production code
- All features must have acceptance tests

### 2. Single Responsibility
- One feature at a time
- Complete current work before starting new
- No feature creep or scope expansion

### 3. Spec-Driven
- Specification before implementation
- Intent drives development, not code
- Changes require spec updates first

## Technical Constraints
- NO new features until 100% tests pass
- MUST use RFD workflow for all fixes
- MUST validate each fix with tests
- NO mock data in tests
- MUST maintain backward compatibility

## What We Will NOT Do
- No premature optimization
- No authentication until core features work
- No frontend until API is complete
- No abstractions until patterns emerge
- No AI-generated code without validation

## Stack Decisions
- Language: python
- Framework: click
- Database: sqlite

## Feature Prioritization
Features must be implemented in order:
1. fix_critical_issues: Fix critical broken functionality preventing RFD from working
2. mock_detection: Mock data detection and prevention system
3. rfd_core_features: Implement missing RFD features for true dogfooding
4. session_manager_fixes: Fix all 6 SessionManager test failures
5. spec_engine_fixes: Fix all 4 SpecEngine test failures
6. integration_test_fixes: Fix 12 integration test failures
7. rfd_dogfooding: Complete RFD dogfooding with installer and automation

## Success Metrics
- All acceptance criteria met
- Zero hallucination incidents
- No mock data in codebase
- 100% feature completion before new work

---
This constitution is immutable. Any changes require unanimous agreement and version bump.
