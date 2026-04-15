"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: typeguard-list-narrowing-refined.py
Patterns detected: 1
    - typeguard_narrowing (6 tests)
Test cases generated: 6
"""

# --- Original source ---

from typing import TypeGuard, List, Union, Literal, reveal_type

# A custom type guard for a list of mixed types
# MODIFIED: The input type of TypeGuard now includes 'float'
# to match the `data` parameter in `process_mixed_data`.
# This resolves the initial 'arg-type' error and pushes the type-checking
# complexity to the narrowing logic itself, which is a common source of divergence.
def has_only_numbers_or_bools(items: List[Union[int, str, bool, float]]) -> TypeGuard[List[Union[int, bool]]]:
    """Narrows a list to contain only numbers or booleans."""
    return all(isinstance(x, (int, bool)) for x in items)

def process_mixed_data(data: List[Union[int, str, bool, float]]):
    # This scenario tests how TypeGuard interacts with lists containing multiple base types
    # and if it correctly narrows a union type within the list elements.
    # The previous error regarding argument type incompatibility for `has_only_numbers_or_bools(data)`
    # should now be resolved, as the TypeGuard's input type has been broadened.
    if has_only_numbers_or_bools(data):
        for item in data:
            # Type checkers might now disagree on the precise narrowed type of 'item'.
            # Expected: 'int | bool' due to the TypeGuard's return annotation.
            # Some checkers might correctly narrow, while others might retain 'str' or 'float'
            # types, or be overly conservative, leading to divergence.
            reveal_type(item)
            print(f"Number or Bool: {item}")
    else:
        for item in data:
            reveal_type(item) # Expected: int | str | bool | float.
            print(f"Mixed item: {item}")

if __name__ == "__main__":
    list_int_bool: List[Union[int, str, bool, float]] = [1, True, 0, False]
    process_mixed_data(list_int_bool)

    list_mixed_str: List[Union[int, str, bool, float]] = [1, "hello", True, 3.14]
    process_mixed_data(list_mixed_str)

    list_mixed_float: List[Union[int, str, bool, float]] = [1, 2.5, True]
    process_mixed_data(list_mixed_float)

    # Type checkers might now disagree on:
    # The precise narrowed type of `item` inside the `if` block (for `reveal_type(item)`).
    # Some checkers are expected to correctly narrow `item` to `int | bool`,
    # while others might retain `str` or `float` from the original union,
    # or apply the narrowing inconsistently within a generic container.

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_has_only_numbers_or_bools_returns_bool():
    """Verify has_only_numbers_or_bools returns a boolean."""
    try:
        result = has_only_numbers_or_bools([])
        if not isinstance(result, bool):
            BUGS.append({"line": 8, "type": "ReturnTypeMismatch", "error": f"TypeGuard has_only_numbers_or_bools returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_has_only_numbers_or_bools_with_none():
    """Call has_only_numbers_or_bools with None."""
    try:
        has_only_numbers_or_bools(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_none"})


def test_has_only_numbers_or_bools_with_ints():
    """Call has_only_numbers_or_bools with list of ints."""
    try:
        result = has_only_numbers_or_bools([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_has_only_numbers_or_bools_with_strings():
    """Call has_only_numbers_or_bools with list of strings."""
    try:
        result = has_only_numbers_or_bools(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_has_only_numbers_or_bools_with_mixed():
    """Call has_only_numbers_or_bools with mixed type list."""
    try:
        result = has_only_numbers_or_bools([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_has_only_numbers_or_bools_with_bools():
    """Call has_only_numbers_or_bools with list of booleans."""
    try:
        result = has_only_numbers_or_bools([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


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
