"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: newtype-typeguard-divergence-refined.py
Patterns detected: 2
    - typeguard_narrowing (6 tests)
  - newtype (4 tests)
Test cases generated: 10
"""

# --- Original source ---

from typing import NewType, Union, TypeGuard
from typing_extensions import reveal_type

SensorReading = NewType("SensorReading", float)
DeviceId = NewType("DeviceId", int)
StatusCode = NewType("StatusCode", int)

MixedValues = Union[SensorReading, DeviceId, StatusCode, str, bool, float, int]

# This TypeGuard is designed to create divergence.
# It checks for base types (int, float) but promises to narrow to a Union
# that includes the NewType wrappers (SensorReading, DeviceId, StatusCode)
# along with raw int and float.
#
# Divergence is expected here because:
# - Mypy/Pyright: When `isinstance(val, (int, float))` is true, they typically
#   narrow `val` to its base type `int | float`, losing the `NewType` wrapper
#   information (DeviceId, StatusCode, SensorReading). Thus, `x` inside the
#   comprehension would be inferred as `int | float`.
# - Other checkers (e.g., Zuban, Pyrefly, Ty): Might respect the TypeGuard's
#   return annotation more literally, inferring `x` as the full promised type
#   `Union[SensorReading, DeviceId, StatusCode, float, int]`, even though the
#   runtime `isinstance` check doesn't preserve `NewType` distinctions.
def is_numeric_and_newtype_like(val: MixedValues) -> TypeGuard[Union[SensorReading, DeviceId, StatusCode, float, int]]:
    # At runtime, `isinstance(val, (int, float))` will be true for all
    # SensorReading, DeviceId, StatusCode instances (as they are just floats/ints),
    # as well as raw float and int values.
    # The ambiguity lies in how type checkers propagate the `NewType` information
    # through this TypeGuard when the runtime check is on the base type.
    return isinstance(val, (int, float))

if __name__ == "__main__":
    raw_data: list[MixedValues] = [
        SensorReading(10.5),
        DeviceId(101),
        "error",
        True,
        StatusCode(200),
        DeviceId(102),
        15.0, # raw float
        300,  # raw int
    ]

    # This comprehension applies the `is_numeric_and_newtype_like` TypeGuard.
    # The type revealed for `x` and the final `filtered_values_set` is the
    # expected point of divergence.
    filtered_values_set = {
        reveal_type(x) # EXPECTED DIVERGENCE:
                       # Mypy/Pyright might reveal: 'builtins.float | builtins.int'
                       # Others might reveal: 'Union[SensorReading, DeviceId, StatusCode, float, int]'
        for x in raw_data
        if is_numeric_and_newtype_like(x)
    }
    reveal_type(filtered_values_set) # EXPECTED DIVERGENCE:
                                     # Mypy/Pyright might reveal: 'set[builtins.float | builtins.int]'
                                     # Others might reveal: 'set[Union[SensorReading, DeviceId, StatusCode, float, int]]'

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_is_numeric_and_newtype_like_returns_bool():
    """Verify is_numeric_and_newtype_like returns a boolean."""
    try:
        result = is_numeric_and_newtype_like([])
        if not isinstance(result, bool):
            BUGS.append({"line": 24, "type": "ReturnTypeMismatch", "error": f"TypeGuard is_numeric_and_newtype_like returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_is_numeric_and_newtype_like_with_none():
    """Call is_numeric_and_newtype_like with None."""
    try:
        is_numeric_and_newtype_like(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_none"})


def test_is_numeric_and_newtype_like_with_ints():
    """Call is_numeric_and_newtype_like with list of ints."""
    try:
        result = is_numeric_and_newtype_like([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_is_numeric_and_newtype_like_with_strings():
    """Call is_numeric_and_newtype_like with list of strings."""
    try:
        result = is_numeric_and_newtype_like(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_is_numeric_and_newtype_like_with_mixed():
    """Call is_numeric_and_newtype_like with mixed type list."""
    try:
        result = is_numeric_and_newtype_like([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_is_numeric_and_newtype_like_with_bools():
    """Call is_numeric_and_newtype_like with list of booleans."""
    try:
        result = is_numeric_and_newtype_like([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


def test_DeviceId_from_int():
    """Create DeviceId from a plain int."""
    try:
        val = DeviceId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_DeviceId_from_string():
    """Create DeviceId from a string (wrong base type)."""
    try:
        val = DeviceId("not_an_int")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_StatusCode_from_int():
    """Create StatusCode from a plain int."""
    try:
        val = StatusCode(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_StatusCode_from_string():
    """Create StatusCode from a string (wrong base type)."""
    try:
        val = StatusCode("not_an_int")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
