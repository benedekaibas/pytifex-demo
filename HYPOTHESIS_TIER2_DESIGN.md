# Hypothesis-Based Tier 2 Design Document

## Executive Summary

The Tier 2 evaluation has been completely rewritten to use **Hypothesis property-based testing** instead of manual mutation. This provides:

- **Rigorous type-aware value generation** via Hypothesis strategies
- **Full source context** in every test (no orphaned code snippets)
- **Clear pass/fail semantics** with explicit assertions
- **Reproducible test artifacts** suitable for research publication
- **Semantic understanding** of complex types (NewType, TypedDict, Protocol)

## Motivation: Problems with Manual Mutation

The original Tier 2 used manual mutation with several critical flaws:

### 1. Generic Violations Don't Reflect Reality
```python
# Old approach: generate_violating_values() for TypedDict
violations = [({}, "empty dict (missing required keys)")]
```

**Problem**: An empty dict `{}` is often a valid violation, but what if:
- The TypedDict has no required keys?
- The field is `NotRequired`?
- The code doesn't actually access the missing key?

The mutation doesn't understand the schema, so verdicts are uncertain.

### 2. Orphaned Code Snippets Lose Context
```python
# Old approach: test is created without original imports/definitions
test_code = """
from typeguard import check_type
value = {}
check_type(value, TypedDict(...))  # NameError: TypedDict not defined!
"""
```

**Problem**: The test imports are minimal and brittle. Dependencies, custom types, and context are lost.

### 3. Silent Passes = Uncertain Verdicts
```python
# Old approach: no assertion logic
try:
    exec(compile(test_code, "<typeguard_test>", "exec"), {})
    # ... what now? Test passed or failed?
except Exception:
    # Maybe a real error, maybe a setup error
    bugs.append(...)
```

**Problem**: Without explicit assertions, it's impossible to distinguish:
- A type violation that was correctly caught (✓)
- A type violation that was silently ignored (✗)
- A setup error in the test harness (?)

### 4. No Semantic Understanding of Complex Types
- NewType is treated as a generic unknown type
- Protocols require structural analysis
- TypedDict key requirements aren't inspected
- Union types are oversimplified

## New Approach: Hypothesis-Based Testing

### Core Architecture

```python
hypothesis_tier2.py
├── TypeStrategyBuilder
│   ├── from_annotation(str) → (valid_strategy, invalid_strategy)
│   └── type-specific extractors
│       ├── _extract_literal_values()
│       ├── _extract_generic_arg()
│       └── _extract_newtype_base()
│
├── HypothesisTestHarness
│   ├── __init__(source_code, output_dir)
│   ├── test_annotation(annotation, line, variable_name)
│   ├── _run_valid_test()
│   ├── _run_invalid_test()
│   └── save_test_file()
│
└── run_hypothesis_tier2(source_code, annotations, checker_outputs)
    ├── extract annotations if needed
    ├── identify disagreement lines
    ├── filter to target annotations
    └── run harness for each annotation
```

### Type-Aware Strategy Generation

Each supported type has both a **valid strategy** and an **invalid strategy**:

| Type | Valid | Invalid | Notes |
|------|-------|---------|-------|
| `int` | `st.integers()` | text/float/None | Comprehensive coverage |
| `str` | `st.text()` | int/float/None | Includes edge cases |
| `float` | `st.floats()` | text/None | Excludes NaN/infinity |
| `bool` | `st.booleans()` | text/int | Correct type semantics |
| `List[T]` | `st.lists(T_strategy)` | text/int/dict | Size and element variation |
| `Dict[K,V]` | `st.dicts(K, V)` | text/list | Preserves key/value types |
| `Optional[T]` | `st.none()` | other | Tests nullable semantics |
| `Literal[a, b]` | `st.sampled_from([a,b])` | other | Exhaustive literal set |
| `NewType('N', T)` | Delegates to T | Delegates to T | Unwraps to base type |
| Custom classes | `st.just({})` | text | Generic object handling |

### Test Execution Pattern

For each annotation:

```python
# Step 1: Extract strategies
valid_strat, invalid_strat = TypeStrategyBuilder.from_annotation("int")

# Step 2: Run valid test (sanity check)
harness._run_valid_test("int", valid_strat, "x")
# Expected: No errors (constraint allows these values)

# Step 3: Run invalid test (constraint enforcement check)
harness._run_invalid_test("int", invalid_strat, "x")
# Expected: Error! (constraint should reject invalid values)

# Step 4: Interpret results
if invalid_test_crashed:
    # ✓ Constraint is enforced at runtime
    # Type checkers that miss this are INCORRECT
else:
    # ✗ Constraint has no runtime effect
    # UNCERTAIN whether type checkers should flag it
```

### Full Source Context

Every test includes the complete source code:

```python
# Generated test file (hypothesis_invalid_int.py)
"""Hypothesis-based property test for type constraint validation.

Type annotation: int
Test type: invalid
"""

# Original source code - COMPLETE
x: int = 42
def foo(y: int) -> int:
    return y + 1

# Test harness
from hypothesis import given, strategies as st
from typeguard import check_type, TypeCheckError
from beartype import beartype

def test_invalid_case(value):
    try:
        check_type(value, int)
        return False  # Not enforced
    except (TypeCheckError, TypeError):
        return True   # Enforced!

# Run test
if not test_invalid_case("not an int"):
    raise AssertionError("Type constraint not enforced")
```

## Implementation Details

### TypeStrategyBuilder

```python
class TypeStrategyBuilder:
    @staticmethod
    def from_annotation(annotation: str) -> Optional[tuple]:
        """
        Returns (valid_strategy, invalid_strategy) for the given annotation.
        
        Returns None if unsupported type.
        """
```

**Key methods**:
- `from_annotation(str)`: Main entry point, returns strategy pair
- `_extract_generic_arg(annotation)`: Parse `List[T]` → `T`
- `_extract_literal_values(annotation)`: Parse `Literal[1, "x", True]` → values
- `_extract_newtype_base(annotation)`: Parse `NewType('N', int)` → `int`

**Design pattern**: Each type builds strategies that:
1. **Valid strategy**: Generates values that satisfy the type
2. **Invalid strategy**: Generates values that violate it
3. Both are deterministic and reproducible

### HypothesisTestHarness

```python
class HypothesisTestHarness:
    def __init__(self, source_code: str, output_dir: Optional[str]):
        self.source_code = source_code  # Full context included
        self.output_dir = output_dir    # Where to save test files
    
    def test_annotation(annotation, line, variable_name) -> HypothesisTestResult:
        """
        Test a single annotation with Hypothesis.
        
        Returns HypothesisTestResult with:
        - passed: Whether constraint is enforced
        - failure_type: "no_enforcement" if not enforced
        - test_cases_count: Number of Hypothesis tests run
        - reproducible_seed: For deterministic replay
        """
```

**Execution flow**:
1. Build valid/invalid strategies from annotation
2. Run valid test (sanity check for test setup)
3. Run invalid test (enforcement check)
4. Save test files to `output_dir` for inspection
5. Return result indicating if constraint matters

### Integration with Tier 1 and 3

```
Tier 1 (Runtime Crashes)
    ↓ (finds runtime exceptions)
    ↓
Tier 2 (Hypothesis Testing) ← YOU ARE HERE
    ↓ (confirms constraints matter)
    ↓
Tier 3 (PEP Specification)
    ↓ (checks alignment with standards)
    ↓
Final Verdict (CORRECT/INCORRECT/UNCERTAIN)
```

**Tier 2's role**:
- **Input**: Tier 1 output (runtime bugs), source code, annotations
- **Processing**: Generate type-aware test cases, execute with enforcement
- **Output**: Confirmation that constraints actually matter at runtime
- **Feeds to Tier 3**: If constraint doesn't matter, might explain disagreements

## Migration from Old Tier 2

### Old Pattern (comprehensive_eval.py)
```python
def run_tier2(source_code, annotations, checker_outputs=None, debug=None):
    for ann in annotations:
        violations = generate_violating_values(ann.annotation)  # Generic
        for violating_value, description in violations:
            test_code = _create_typeguard_test(ann, violating_value, source_imports)
            crashed, error_msg = _run_typeguard_test(test_code)
            if crashed:
                bugs.append(TypeBug(...))
```

**Issues**:
- `generate_violating_values()` is too generic
- Test has no source context
- No semantic understanding of types
- Silent pass logic is unclear

### New Pattern (hypothesis_tier2.py)
```python
def run_hypothesis_tier2(source_code, annotations=None, checker_outputs=None, output_dir=None):
    annotations = annotations or extract_type_annotations(source_code)
    harness = HypothesisTestHarness(source_code, output_dir)
    
    for ann in annotations:
        result = harness.test_annotation(ann.annotation, ann.line, ann.variable_name)
        if not result.passed:
            bugs.append(TypeBug(...))
```

**Improvements**:
- Full source context in every test
- Type-aware strategy generation
- Explicit pass/fail semantics
- Reproducible test artifacts
- Semantic understanding of complex types

## Output and Artifacts

### TypeBug Records

```python
TypeBug(
    line=42,
    bug_type="ConstraintNotEnforced",
    message="Type constraint not enforced at runtime: Violations did not cause runtime errors",
    source="hypothesis_tier2",
    confidence=0.85,
    details={
        "annotation": "int",
        "variable": "x",
        "test_cases": 10,
        "failure_type": "no_enforcement"
    }
)
```

### Saved Test Files

Saved to `{output_dir}/hypothesis_{test_type}_{sanitized_annotation}.py`:

```python
# hypothesis_invalid_int.py
"""Hypothesis-based property test for type constraint validation.

Type annotation: int
Test type: invalid
"""

x: int = 42
def foo(y: int) -> int:
    return y + 1

from hypothesis import given, strategies as st
from typeguard import check_type, TypeCheckError
from beartype import beartype

@beartype
def test_invalid_case(value):
    try:
        check_type(value, int)
        return False
    except (TypeCheckError, TypeError):
        return True

# Run test
if not test_invalid_case("not an int"):
    raise AssertionError("Type constraint not enforced")
```

These files are:
- **Self-contained**: Include all necessary imports and context
- **Reproducible**: Can be re-run independently
- **Publication-ready**: Suitable for research papers
- **Verifiable**: Other researchers can inspect and validate

## Testing Checklist

When integrating with comprehensive_eval.py:

- [ ] Extract and test all type annotations
- [ ] Focus on annotations near disagreement lines
- [ ] Handle unsupported types gracefully (return None strategy)
- [ ] Save test files to `debug/` folders for inspection
- [ ] Track test case counts for statistical confidence
- [ ] Integrate TypeBug results with Tier 3 analysis
- [ ] Verify Tier 1 + Tier 2 + Tier 3 pipeline works end-to-end

## Future Enhancements

1. **Hypothesis RecordingProvider**: Capture exact values used in failures for replay
2. **Property Invariants**: Generate multiple related assertions for richer testing
3. **Coverage Tracking**: Measure which code paths hypothesis explores
4. **Mutation Analysis**: If a mutation doesn't change test results, constraint is fragile
5. **Type Inference**: Analyze type flow to infer which values are semantically valid
6. **Schema Extraction**: Inspect actual TypedDict definitions at runtime for key analysis

## References

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Typeguard Runtime Type Checking](https://typeguard.readthedocs.io/)
- [Beartype Type Enforcement](https://beartype.readthedocs.io/)
- [PEP 484: Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 589: TypedDict](https://www.python.org/dev/peps/pep-0589/)
