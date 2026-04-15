"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: match-typeguard-generic-tuple.py
Patterns detected: 2
    - tuple_length (15 tests)
  - typeguard_narrowing (12 tests)
Test cases generated: 27
"""

# --- Original source ---

import typing as t
from typing import TypeGuard, TypeVar, Union, Tuple, Any

T = TypeVar("T")
S = TypeVar("S")

def is_str_pair(val: Tuple[Any, Any]) -> TypeGuard[Tuple[str, str]]:
    """TypeGuard to check if a tuple contains two strings."""
    return isinstance(val, tuple) and len(val) == 2 and isinstance(val[0], str) and isinstance(val[1], str)

def is_int_bool_pair(val: Tuple[Any, Any]) -> TypeGuard[Tuple[int, bool]]:
    """TypeGuard to check if a tuple contains an int and a bool."""
    return isinstance(val, tuple) and len(val) == 2 and isinstance(val[0], int) and isinstance(val[1], bool)


def process_item[X, Y](item: Union[Tuple[int, bool], Tuple[str, str], Tuple[X, Y]]) -> str:
    reveal_type(item) # Should be Union[Tuple[int, bool], Tuple[str, str], Tuple[X, Y]]
    match item:
        case (a, b) if is_str_pair(item): # Mypy might not correctly narrow 'a' and 'b' to str
            reveal_type(a) # Expected: str
            reveal_type(b) # Expected: str
            return f"String pair: {a}, {b}"
        case (x, y) if is_int_bool_pair(item): # Mypy might not correctly narrow 'x' and 'y' to int, bool
            reveal_type(x) # Expected: int
            reveal_type(y) # Expected: bool
            return f"Int-bool pair: {x}, {y}"
        case (p, q): # General case for Tuple[X, Y] if not narrowed
            reveal_type(p) # Expected: X
            reveal_type(q) # Expected: Y
            return f"Generic pair: {p} ({type(p).__name__}), {q} ({type(q).__name__})"

if __name__ == "__main__":
    print(process_item((1, True)))
    print(process_item(("hello", "world")))
    print(process_item((3.14, None))) # X=float, Y=None
    
    # Test with a specific generic tuple type, that should hit the generic case
    my_generic_tuple: Tuple[float, int] = (1.5, 2)
    print(process_item(my_generic_tuple))

    # Test with mixed types not caught by guards
    mixed_tuple = (1, "mixed")
    print(process_item(mixed_tuple))

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_is_str_pair_empty_tuple():
    """Call is_str_pair with empty tuple for param 'val'."""
    try:
        is_str_pair(val=())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "empty_tuple"})


def test_is_str_pair_single_element_tuple():
    """Call is_str_pair with single-element tuple for param 'val'."""
    try:
        is_str_pair(val=(1,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "single_element_tuple"})


def test_is_str_pair_none_in_tuple():
    """Call is_str_pair with None element in tuple for param 'val'."""
    try:
        is_str_pair(val=(None,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "none_in_tuple"})


def test_is_str_pair_wrong_types_in_tuple():
    """Call is_str_pair with wrong types in tuple for param 'val'."""
    try:
        is_str_pair(val=(123, 456, 789))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_types_in_tuple"})


def test_is_str_pair_string_instead_of_tuple():
    """Call is_str_pair with a string instead of tuple for param 'val'."""
    try:
        is_str_pair(val="not a tuple")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "string_instead_of_tuple"})


def test_is_int_bool_pair_empty_tuple():
    """Call is_int_bool_pair with empty tuple for param 'val'."""
    try:
        is_int_bool_pair(val=())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "empty_tuple"})


def test_is_int_bool_pair_single_element_tuple():
    """Call is_int_bool_pair with single-element tuple for param 'val'."""
    try:
        is_int_bool_pair(val=(1,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "single_element_tuple"})


def test_is_int_bool_pair_none_in_tuple():
    """Call is_int_bool_pair with None element in tuple for param 'val'."""
    try:
        is_int_bool_pair(val=(None,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "none_in_tuple"})


def test_is_int_bool_pair_wrong_types_in_tuple():
    """Call is_int_bool_pair with wrong types in tuple for param 'val'."""
    try:
        is_int_bool_pair(val=(123, 456, 789))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_types_in_tuple"})


def test_is_int_bool_pair_string_instead_of_tuple():
    """Call is_int_bool_pair with a string instead of tuple for param 'val'."""
    try:
        is_int_bool_pair(val="not a tuple")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "string_instead_of_tuple"})


def test_process_item_empty_tuple():
    """Call process_item with empty tuple for param 'item'."""
    try:
        process_item(item=())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "empty_tuple"})


def test_process_item_single_element_tuple():
    """Call process_item with single-element tuple for param 'item'."""
    try:
        process_item(item=(1,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "single_element_tuple"})


def test_process_item_none_in_tuple():
    """Call process_item with None element in tuple for param 'item'."""
    try:
        process_item(item=(None,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "none_in_tuple"})


def test_process_item_wrong_types_in_tuple():
    """Call process_item with wrong types in tuple for param 'item'."""
    try:
        process_item(item=(123, 456, 789))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_types_in_tuple"})


def test_process_item_string_instead_of_tuple():
    """Call process_item with a string instead of tuple for param 'item'."""
    try:
        process_item(item="not a tuple")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "string_instead_of_tuple"})


def test_is_str_pair_returns_bool():
    """Verify is_str_pair returns a boolean."""
    try:
        result = is_str_pair([])
        if not isinstance(result, bool):
            BUGS.append({"line": 7, "type": "ReturnTypeMismatch", "error": f"TypeGuard is_str_pair returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_is_str_pair_with_none():
    """Call is_str_pair with None."""
    try:
        is_str_pair(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_none"})


def test_is_str_pair_with_ints():
    """Call is_str_pair with list of ints."""
    try:
        result = is_str_pair([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_is_str_pair_with_strings():
    """Call is_str_pair with list of strings."""
    try:
        result = is_str_pair(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_is_str_pair_with_mixed():
    """Call is_str_pair with mixed type list."""
    try:
        result = is_str_pair([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_is_str_pair_with_bools():
    """Call is_str_pair with list of booleans."""
    try:
        result = is_str_pair([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


def test_is_int_bool_pair_returns_bool():
    """Verify is_int_bool_pair returns a boolean."""
    try:
        result = is_int_bool_pair([])
        if not isinstance(result, bool):
            BUGS.append({"line": 11, "type": "ReturnTypeMismatch", "error": f"TypeGuard is_int_bool_pair returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_is_int_bool_pair_with_none():
    """Call is_int_bool_pair with None."""
    try:
        is_int_bool_pair(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_none"})


def test_is_int_bool_pair_with_ints():
    """Call is_int_bool_pair with list of ints."""
    try:
        result = is_int_bool_pair([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_is_int_bool_pair_with_strings():
    """Call is_int_bool_pair with list of strings."""
    try:
        result = is_int_bool_pair(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_is_int_bool_pair_with_mixed():
    """Call is_int_bool_pair with mixed type list."""
    try:
        result = is_int_bool_pair([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_is_int_bool_pair_with_bools():
    """Call is_int_bool_pair with list of booleans."""
    try:
        result = is_int_bool_pair([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 11, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


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
