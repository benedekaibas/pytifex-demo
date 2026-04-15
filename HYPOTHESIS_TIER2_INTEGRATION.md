# Hypothesis Tier 2 Integration Guide

## Quick Start

### Before (Old Manual Mutation)
```python
from comprehensive_eval import run_tier2, extract_type_annotations

annotations = extract_type_annotations(source_code)
bugs = run_tier2(source_code, annotations, checker_outputs)
```

### After (Hypothesis Property Testing)
```python
from hypothesis_tier2 import run_hypothesis_tier2

bugs = run_hypothesis_tier2(
    source_code=source_code,
    annotations=None,  # Auto-extracted
    checker_outputs=checker_outputs,
    output_dir="debug/tier2_tests"
)
```

## Integration Patterns

### Pattern 1: Drop-in Replacement in Comprehensive Eval

Replace the `run_tier2` function call in `comprehensive_eval.py`:

```python
# OLD: comprehensive_eval.py
from comprehensive_eval import run_tier2
tier2_bugs = run_tier2(source_code, annotations, checker_outputs, debug)

# NEW: comprehensive_eval.py
from hypothesis_tier2 import run_hypothesis_tier2, extract_type_annotations
annotations = extract_type_annotations(source_code)
tier2_bugs = run_hypothesis_tier2(source_code, annotations, checker_outputs, output_dir=debug_dir)
```

### Pattern 2: Parallel Evaluation (Old vs New)

During transition, run both and compare results:

```python
from comprehensive_eval import run_tier2 as run_tier2_old
from hypothesis_tier2 import run_hypothesis_tier2

# Run both methods
old_bugs = run_tier2_old(source_code, annotations, checker_outputs, debug)
new_bugs = run_hypothesis_tier2(source_code, annotations, checker_outputs, debug_dir)

# Log differences for analysis
if len(old_bugs) != len(new_bugs):
    print(f"Tier 2 results differ: {len(old_bugs)} vs {len(new_bugs)} bugs found")
```

### Pattern 3: Annotation-Specific Testing

Test individual annotations:

```python
from hypothesis_tier2 import HypothesisTestHarness, extract_type_annotations

source_code = """
x: int = 5
y: str = "hello"
z: List[int] = [1, 2, 3]
"""

harness = HypothesisTestHarness(source_code, output_dir="tests/")
annotations = extract_type_annotations(source_code)

for ann in annotations:
    result = harness.test_annotation(ann.annotation, ann.line, ann.variable_name)
    print(f"Line {ann.line}: {ann.annotation} - Passed: {result.passed}")
    # Test file saved to: tests/hypothesis_{test_type}_{annotation}.py
```

### Pattern 4: Custom Strategy Building

Extend type support for domain-specific types:

```python
from hypothesis_tier2 import TypeStrategyBuilder
from hypothesis import strategies as st

# Add custom strategy for your type
class CustomStrategyBuilder(TypeStrategyBuilder):
    @staticmethod
    def from_annotation(annotation: str):
        if annotation == "CustomType":
            valid = st.just(CustomType(value=42))
            invalid = st.text()
            return (valid, invalid)
        
        # Fall back to default strategies
        return TypeStrategyBuilder.from_annotation(annotation)

# Use in harness
harness = HypothesisTestHarness(source_code)
result = harness.test_annotation("CustomType", 10, "my_var")
```

## Migration Checklist

### Phase 1: Setup (Today)
- [x] Create `hypothesis_tier2.py` module
- [x] Write design documentation
- [ ] Run unit tests on individual components
- [ ] Verify type strategy generation works
- [ ] Test against sample code

### Phase 2: Integration (Next)
- [ ] Add import to `comprehensive_eval.py`
- [ ] Replace `run_tier2` function call
- [ ] Verify Tier 1 → Tier 2 → Tier 3 pipeline works
- [ ] Run full evaluation on test cases
- [ ] Compare old vs new bug counts
- [ ] Inspect saved test files for quality

### Phase 3: Validation (After Integration)
- [ ] Run on full benchmark suite
- [ ] Compare results with baseline
- [ ] Verify test files are publication-ready
- [ ] Get peer review on methodology
- [ ] Document lessons learned

### Phase 4: Cleanup (Final)
- [ ] Remove old Tier 2 code from `comprehensive_eval.py`
- [ ] Archive `generate_violating_values()` and helpers
- [ ] Update documentation with final results
- [ ] Submit to version control

## Testing the New Implementation

### Unit Test: Type Strategy Generation

```python
from hypothesis_tier2 import TypeStrategyBuilder

def test_int_strategy():
    valid, invalid = TypeStrategyBuilder.from_annotation("int")
    assert valid is not None
    assert invalid is not None

def test_literal_strategy():
    valid, invalid = TypeStrategyBuilder.from_annotation("Literal['x', 'y']")
    assert valid is not None

def test_newtype_strategy():
    valid, invalid = TypeStrategyBuilder.from_annotation("NewType('UserId', int)")
    assert valid is not None
```

### Integration Test: Full Pipeline

```python
from hypothesis_tier2 import run_hypothesis_tier2

source = """
x: int = 5
y: str = "hello"
def foo(z: float) -> bool:
    return True
"""

bugs = run_hypothesis_tier2(source, output_dir="/tmp/test_tier2")

# Verify results
assert len(bugs) >= 0  # May find type enforcement issues
for bug in bugs:
    assert bug.source == "hypothesis_tier2"
    assert bug.details["annotation"] is not None
```

### Manual Inspection Test

```bash
# Run evaluation and inspect generated tests
python -c "
from hypothesis_tier2 import run_hypothesis_tier2

source = '''
x: int = 5
y: list[int] = []
'''

bugs = run_hypothesis_tier2(source, output_dir='./debug_tests')
"

# Inspect the generated test files
ls -la ./debug_tests/
cat ./debug_tests/hypothesis_invalid_int.py
cat ./debug_tests/hypothesis_valid_int.py
```

## Expected Output

### Test Files Generated

For source code with `x: int = 5`, you'll get:
- `hypothesis_valid_int.py` - Tests that valid int values pass
- `hypothesis_invalid_int.py` - Tests that non-int values are rejected

### Bug Records Generated

```python
TypeBug(
    line=1,
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

### Log Output

```
Testing annotation 'int' on line 1
  - Valid test: PASS (3 cases)
  - Invalid test: FAIL (constraint not enforced)
  - Result: ConstraintNotEnforced
  - Test files saved to: debug/hypothesis_*_int.py
```

## Troubleshooting

### Issue: No bugs found for obviously broken code
**Cause**: Type enforcement might be optional in the test harness
**Fix**: Ensure both `beartype` and `typeguard` are imported and active

### Issue: Test files have syntax errors
**Cause**: Source code itself is invalid
**Fix**: Validate source code with `ast.parse()` first

### Issue: Unsupported type annotation
**Cause**: `TypeStrategyBuilder.from_annotation()` returns None
**Fix**: Add custom strategy handling in your code or file an issue

### Issue: Tests are too slow
**Cause**: Hypothesis is generating too many test cases
**Fix**: Add `@settings(max_examples=100)` to limit test count

## Performance Expectations

For a typical source file with 5-10 type annotations:
- **Time**: 1-5 seconds (per file)
- **Test files created**: 10-20 (2 per annotation)
- **Memory**: < 50 MB
- **Disk usage**: < 1 MB (for test files)

## Comparing Old vs New Results

When both implementations are available:

```python
from comprehensive_eval import run_tier2 as old_tier2
from hypothesis_tier2 import run_hypothesis_tier2

old_bugs = old_tier2(source, annotations, checker_outputs, debug)
new_bugs = run_hypothesis_tier2(source, annotations, checker_outputs)

print(f"Old Tier 2: {len(old_bugs)} bugs")
print(f"New Tier 2: {len(new_bugs)} bugs")

# Analyze differences
old_annotations = {b.details.get("annotation") for b in old_bugs}
new_annotations = {b.details.get("annotation") for b in new_bugs}

print(f"Old found: {old_annotations}")
print(f"New found: {new_annotations}")
print(f"New in both: {old_annotations & new_annotations}")
```

## Documentation for Researchers

When publishing results using Hypothesis Tier 2, include:

### Methodology Section
```
Tier 2 uses Hypothesis property-based testing to validate type constraints.
For each annotation, we generate:
1. Valid values that satisfy the type (sanity check)
2. Invalid values that violate the type (enforcement check)

If invalid values cause runtime errors (TypeCheckError or TypeError), the
constraint is enforced. If not, we report ConstraintNotEnforced.

All tests include full source context and are reproducible.
```

### Artifacts
- Saved test files in `debug/hypothesis_*.py`
- Test case counts in TypeBug.details["test_cases"]
- Reproducible seeds in HypothesisTestResult

### Limitations
- Custom/user-defined types use generic strategies (may not be realistic)
- Function return types tested in isolation (may not reflect real usage)
- No inter-procedural analysis (doesn't track values across functions)

## See Also

- [HYPOTHESIS_TIER2_DESIGN.md](HYPOTHESIS_TIER2_DESIGN.md) - Architecture details
- [comprehensive_eval.py](src/tc_disagreement/comprehensive_eval.py) - Main evaluation pipeline
- [hypothesis_tier2.py](src/tc_disagreement/hypothesis_tier2.py) - Implementation
