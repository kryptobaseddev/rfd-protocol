---
description: Cross-artifact consistency and coverage analysis
allowed-tools: Bash(*), Read(*), Grep(*), TodoWrite
---

# RFD Analyze - Cross-Artifact Consistency Check

This command performs comprehensive analysis across all project artifacts to ensure consistency and alignment, similar to spec-kit's /analyze functionality.

## Analysis Checks

1. **Spec Alignment**: Verify code matches .rfd/config.yaml specifications
2. **Task Consistency**: Check task completion vs feature status  
3. **API Implementation**: Validate API contracts are implemented
4. **Test Coverage**: Ensure acceptance criteria have tests
5. **Constitution Adherence**: Check immutable principles are followed
6. **Phase Dependencies**: Verify proper phase ordering
7. **Integrity**: Check for hallucinations and drift

## Execute Analysis

Run the comprehensive cross-artifact analysis:

!rfd analyze

## Interpretation

- **Overall Health**:
  - `healthy`: All checks passed
  - `warning`: Minor issues found
  - `critical`: Major inconsistencies detected

- **Coverage Thresholds**:
  - API Implementation: Should be 100%
  - Test Coverage: Should be >80%
  - Task Completion: Should match feature status

## Next Steps

Based on the analysis results:
1. Fix any critical issues first
2. Address spec misalignments
3. Complete missing API implementations
4. Add tests for uncovered acceptance criteria
5. Resolve constitution violations

Track all fixes with TodoWrite for visibility.