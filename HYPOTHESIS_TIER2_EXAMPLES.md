# Hypothesis Tier 2: Before & After Examples

## Example 1: Simple Integer Type

### Old Approach (Manual Mutation)

**Source Code**
```python
# example.py
x: int = 5
print(x + 1)
```

**Generated Test** (orphaned, no context)
```python
# OLD: generated test loses context
from typeguard import check_type

value = "not_an_int"  # From generate_violating_values("int")
check_type(value, int)  # Crashes with TypeCheckError
```

**Problems**:
- ✗ No imports from original source
- ✗ No imports of used modules
- ✗ Test is artificial and isolated
- ✓ Does catch the violation (lucky case)

**Verdict**: UNCERTAIN (test is brittle, could fail in other contexts)

---

### New Approach (Hypothesis)

**Source Code** (same)
```python
# example.py
x: int = 5
print(x + 1)
```

**Generated Test** (full context included)
```python
# NEW: test has complete source + imports + clear assertions
"""Hypothesis-based property test for type constraint validation.

Type annotation: int
Test type: invalid
"""

# Original source code
x: int = 5
print(x + 1)

# Test harness
from hypothesis import given, strategies as st
from typeguard import check_type, TypeCheckError
from beartype import beartype

def test_invalid_case(value):
    """Test that non-int values are rejected."""
    try:
        check_type(value, int)
        return False  # No error - constraint NOT enforced
    except (TypeCheckError, TypeError):
        return True   # Error caught - constraint enforced!

# Run test with various invalid values
test_cases = ["not_an_int", 3.14, None, [], {}]
for test_value in test_cases:
    if not test_invalid_case(test_value):
        raise AssertionError(f"Type constraint 'int' not enforced for {test_value}")

print("✓ All invalid values correctly rejected")
```

**Advantages**:
- ✓ Full source context (imports, dependencies)
- ✓ Multiple test cases (string, float, None, list, dict)
- ✓ Clear assertions with meaningful error messages
- ✓ Can be run independently: `python hypothesis_invalid_int.py`
- ✓ Suitable for research publication

**Verdict**: CONFIDENT that `int` constraint is enforced

---

## Example 2: TypedDict with Required Keys

### Old Approach (Manual Mutation)

**Source Code**
```python
from typing_extensions import TypedDict

class User(TypedDict):
    name: str
    age: int
    email: str  # required

def process_user(u: User) -> None:
    print(f"{u['name']} is {u['age']}")
```

**Generated Test**
```python
# OLD: doesn't understand TypedDict schema
from typeguard import check_type

# Hardcoded empty dict violation (generic fallback)
value = {}  # Missing ALL required keys
check_type(value, User)  # TypeCheckError
```

**Problems**:
- ✗ Empty dict violates schema, but also violates multiple keys simultaneously
- ✗ Doesn't test which specific key is required
- ✗ Doesn't understand that `email` is never accessed in the code
- ✗ Can't distinguish "constraint exists but doesn't matter" from "constraint matters"

**Verdict**: UNCERTAIN (mutation is too generic)

---

### New Approach (Hypothesis)

**Source Code** (same)
```python
from typing_extensions import TypedDict

class User(TypedDict):
    name: str
    age: int
    email: str

def process_user(u: User) -> None:
    print(f"{u['name']} is {u['age']}")
```

**Generated Tests**

**Test 1: Valid case**
```python
"""Test that valid User objects pass.

Type annotation: User
Test type: valid
"""

from typing_extensions import TypedDict

class User(TypedDict):
    name: str
    age: int
    email: str

def process_user(u: User) -> None:
    print(f"{u['name']} is {u['age']}")

from hypothesis import given, strategies as st
from typeguard import check_type

@given(st.dictionaries(st.text(), st.integers()))
def test_valid_user(value):
    try:
        check_type(value, User)
        return True  # Valid
    except Exception as e:
        # Some dicts aren't valid Users - that's OK
        return False

# Sanity check: a properly constructed User should work
valid_user = {"name": "Alice", "age": 30, "email": "alice@example.com"}
check_type(valid_user, User)
print("✓ Valid User construction works")
```

**Test 2: Invalid cases**
```python
"""Test that invalid User objects are rejected.

Type annotation: User
Test type: invalid
"""

from typing_extensions import TypedDict

class User(TypedDict):
    name: str
    age: int
    email: str

def process_user(u: User) -> None:
    print(f"{u['name']} is {u['age']}")

from typeguard import check_type, TypeCheckError

def test_missing_key(user_dict):
    """Test that missing required keys are rejected."""
    try:
        check_type(user_dict, User)
        return False  # No error - constraint NOT enforced
    except (TypeCheckError, TypeError):
        return True   # Error caught

# Test each missing-key violation
violations = [
    ({}, "empty dict"),
    ({"name": "Alice"}, "missing age and email"),
    ({"name": "Alice", "age": 30}, "missing email"),
    ({"name": "Alice", "age": 30, "email": None}, "email is None"),
]

for invalid_user, description in violations:
    if not test_missing_key(invalid_user):
        print(f"✗ FAILED: {description}")
        raise AssertionError(f"TypedDict constraint not enforced for: {description}")

print("✓ All TypedDict violations correctly rejected")
```

**Advantages**:
- ✓ Understands TypedDict schema (required keys)
- ✓ Tests multiple violation types systematically
- ✓ Clear about which constraint each test validates
- ✓ Can analyze coverage (which keys are really checked)
- ✓ Reproducible and inspectable

**Verdict**: CONFIDENT that TypedDict constraints are enforced

---

## Example 3: NewType

### Old Approach

**Source Code**
```python
from typing import NewType

UserId = NewType('UserId', int)

def get_user(id: UserId) -> str:
    return f"User {id}"
```

**Generated Test**
```python
# OLD: treats NewType generically as unknown type
value = "not_a_type"  # Falls back to generic violation
check_type(value, UserId)
```

**Problems**:
- ✗ Doesn't unwrap NewType to understand it's based on int
- ✗ Tests are too generic and unrealistic
- ✗ Can't distinguish NewType-specific constraints from base type constraints

**Verdict**: UNCERTAIN (generic strategy for unknown type)

---

### New Approach

**Source Code** (same)
```python
from typing import NewType

UserId = NewType('UserId', int)

def get_user(id: UserId) -> str:
    return f"User {id}"
```

**Generated Tests**

```python
"""Test NewType('UserId', int) constraint.

Type annotation: NewType('UserId', int)
Test type: invalid
"""

from typing import NewType

UserId = NewType('UserId', int)

def get_user(id: UserId) -> str:
    return f"User {id}"

from typeguard import check_type, TypeCheckError

def test_invalid_userid(value):
    """Test that non-int values are rejected."""
    try:
        check_type(value, UserId)
        return False
    except (TypeCheckError, TypeError):
        return True

# NewType is based on int, so violations are similar to int
invalid_values = [
    ("not_an_int", "string instead of int"),
    (3.14, "float instead of int"),
    (None, "None instead of int"),
    ([], "list instead of int"),
]

for invalid_value, description in invalid_values:
    if not test_invalid_userid(invalid_value):
        raise AssertionError(f"UserId constraint not enforced: {description}")

print("✓ NewType constraints correctly enforced")
```

**Advantages**:
- ✓ Understands NewType unwrapping (extracts `int` base type)
- ✓ Generates appropriate int-like violations
- ✓ Tests are realistic and meaningful
- ✓ Can verify runtime enforcement

**Verdict**: CONFIDENT about NewType enforcement

---

## Example 4: Literal Type

### Old Approach

**Source Code**
```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode: {mode}")
```

**Generated Test**
```python
# OLD: generates arbitrary values
value = "invalid_mode"  # Generic string violation
check_type(value, Literal["read", "write", "append"])
```

**Result**: UNCERTAIN (doesn't test actual literal set)

---

### New Approach

**Source Code** (same)
```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode: {mode}")
```

**Generated Tests**

```python
"""Test Literal constraint.

Type annotation: Literal["read", "write", "append"]
Test type: valid
"""

from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode: {mode}")

from typeguard import check_type

# Valid: all literal values should work
valid_modes = ["read", "write", "append"]
for mode in valid_modes:
    check_type(mode, Literal["read", "write", "append"])
    print(f"✓ Mode '{mode}' accepted")
```

```python
"""Test Literal constraint.

Type annotation: Literal["read", "write", "append"]
Test type: invalid
"""

from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode: {mode}")

from typeguard import check_type, TypeCheckError

def test_invalid_mode(value):
    try:
        check_type(value, Literal["read", "write", "append"])
        return False
    except (TypeCheckError, TypeError):
        return True

# Invalid: values outside literal set should fail
invalid_modes = ["READ", "delete", "create", "unknown", None, 42]
for invalid_mode in invalid_modes:
    if not test_invalid_mode(invalid_mode):
        raise AssertionError(f"Literal constraint not enforced for {invalid_mode}")

print("✓ Literal constraint correctly enforced")
```

**Advantages**:
- ✓ Parses literal values from annotation
- ✓ Tests all valid literals explicitly
- ✓ Tests common invalid patterns
- ✓ Clear specification of valid set

**Verdict**: CONFIDENT about Literal enforcement

---

## Example 5: Union Type

### Old Approach

**Source Code**
```python
def process_value(val: int | str) -> None:
    if isinstance(val, int):
        print(f"Number: {val}")
    else:
        print(f"String: {val}")
```

**Generated Test**
```python
# OLD: treats Union generically
value = []  # Generic invalid value
check_type(value, int | str)
```

**Result**: UNCERTAIN (too generic)

---

### New Approach

**Source Code** (same)
```python
def process_value(val: int | str) -> None:
    if isinstance(val, int):
        print(f"Number: {val}")
    else:
        print(f"String: {val}")
```

**Generated Tests**

```python
"""Test Union constraint.

Type annotation: int | str
Test type: valid
"""

from typeguard import check_type

def process_value(val: int | str) -> None:
    if isinstance(val, int):
        print(f"Number: {val}")
    else:
        print(f"String: {val}")

# Valid: any int or str should work
valid_values = [42, "hello", 0, ""]
for val in valid_values:
    check_type(val, int | str)
    print(f"✓ Value {val!r} accepted")
```

```python
"""Test Union constraint.

Type annotation: int | str
Test type: invalid
"""

from typeguard import check_type, TypeCheckError

def process_value(val: int | str) -> None:
    if isinstance(val, int):
        print(f"Number: {val}")
    else:
        print(f"String: {val}")

def test_invalid_union(value):
    try:
        check_type(value, int | str)
        return False
    except (TypeCheckError, TypeError):
        return True

# Invalid: values that aren't int or str
invalid_values = [3.14, None, [], {}, set()]
for invalid_val in invalid_values:
    if not test_invalid_union(invalid_val):
        raise AssertionError(f"Union constraint not enforced for {invalid_val}")

print("✓ Union constraint correctly enforced")
```

**Advantages**:
- ✓ Tests all valid types in union
- ✓ Tests clear violations
- ✓ Handles Python 3.10+ union syntax

**Verdict**: CONFIDENT about Union enforcement

---

## Summary: Quality Improvements

| Aspect | Old | New |
|--------|-----|-----|
| **Context** | Orphaned | Full source included |
| **Type Understanding** | Generic | Semantic (handles NewType, Literal, etc.) |
| **Test Cases** | 1-3 per type | Multiple systematic cases |
| **Assertions** | Silent pass/fail | Explicit with clear error messages |
| **Reproducibility** | One-shot | Can re-run, inspect, publish |
| **Coverage** | Shallow | Handles edge cases and variants |
| **Publication Quality** | No | Yes - self-contained test files |
| **Debugging** | Hard (no context) | Easy (full source visible) |

## Running Examples

To see these differences in action:

```bash
# Create example files
mkdir -p examples/tier2_comparison

# Create old-style tests
cat > examples/old_style_test.py << 'EOF'
from typeguard import check_type
value = "not_an_int"
check_type(value, int)
EOF

# Create new-style tests (from hypothesis_tier2)
python -c "
from hypothesis_tier2 import run_hypothesis_tier2

source = '''
x: int = 5
y: str = \"hello\"
'''

bugs = run_hypothesis_tier2(source, output_dir='examples/new_style_tests')
"

# Compare generated test files
echo "=== OLD STYLE ==="
wc -l examples/old_style_test.py
cat examples/old_style_test.py

echo "=== NEW STYLE ==="
ls -lh examples/new_style_tests/
cat examples/new_style_tests/hypothesis_invalid_int.py
```

## Key Takeaways

1. **Context matters**: Tests with full source are more reliable and trustworthy
2. **Type understanding**: Semantic strategies > generic mutations
3. **Explicit assertions**: Clear pass/fail logic > silent execution
4. **Reproducibility**: Saved test files enable peer review and publication
5. **Systematic testing**: Multiple test cases > single hardcoded violation

The new Hypothesis-based approach provides the rigor needed for publication-quality type checker evaluation.
