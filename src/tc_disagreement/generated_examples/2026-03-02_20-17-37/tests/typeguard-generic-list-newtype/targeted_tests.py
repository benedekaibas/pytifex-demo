"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: typeguard-generic-list-newtype.py
Patterns detected: 2
    - typeguard_narrowing (10 tests)
  - newtype (5 tests)
Test cases generated: 15
"""

# --- Original source ---

import typing as t
from typing import TypeGuard, TypeVar, NewType, List, Union, cast

UserID = NewType("UserID", str)
ProductID = NewType("ProductID", int)

U = TypeVar("U")

def is_list_of_user_ids(data: List[U]) -> TypeGuard[List[UserID]]:
    """Checks if a list contains only UserID (str) values."""
    # Type checkers might incorrectly infer U here, or struggle with NewType comparison.
    return all(isinstance(item, str) for item in data)

def is_list_of_product_ids(data: List[U]) -> TypeGuard[List[ProductID]]:
    """Checks if a list contains only ProductID (int) values."""
    return all(isinstance(item, int) for item in data)


def process_id_list(input_list: List[Union[UserID, ProductID, float, bool]]) -> str:
    reveal_type(input_list) # Expected: List[Union[UserID, ProductID, float, bool]]

    if is_list_of_user_ids(input_list):
        reveal_type(input_list) # Expected: List[UserID]
        # Type checker should know input_list contains only UserID here.
        first_id = input_list[0] if input_list else UserID("N/A")
        reveal_type(first_id) # Expected: UserID
        return f"List contains User IDs: {input_list} (First: {first_id})"
    
    elif is_list_of_product_ids(input_list):
        reveal_type(input_list) # Expected: List[ProductID]
        # Type checker should know input_list contains only ProductID here.
        first_id = input_list[0] if input_list else ProductID(0)
        reveal_type(first_id) # Expected: ProductID
        return f"List contains Product IDs: {input_list} (First: {first_id})"
    
    else:
        # After narrowing, remaining types should be float or bool.
        reveal_type(input_list) # Expected: List[Union[float, bool]]
        return f"List contains mixed or unhandled types: {input_list}"

if __name__ == "__main__":
    user_ids_list: List[Union[UserID, ProductID, float, bool]] = [UserID("user_A"), UserID("user_B")]
    print(process_id_list(user_ids_list))

    product_ids_list: List[Union[UserID, ProductID, float, bool]] = [ProductID(101), ProductID(102)]
    print(process_id_list(product_ids_list))

    mixed_types_list: List[Union[UserID, ProductID, float, bool]] = [UserID("user_C"), 3.14, True]
    print(process_id_list(mixed_types_list))
    
    empty_list: List[Union[UserID, ProductID, float, bool]] = []
    print(process_id_list(empty_list)) # Should hit one of the guards and print its default 'first_id'

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_is_list_of_user_ids_returns_bool():
    """Verify is_list_of_user_ids returns a boolean."""
    try:
        result = is_list_of_user_ids([])
        if not isinstance(result, bool):
            BUGS.append({"line": 9, "type": "ReturnTypeMismatch", "error": f"TypeGuard is_list_of_user_ids returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 9, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_is_list_of_user_ids_with_ints():
    """Call is_list_of_user_ids with list of ints."""
    try:
        result = is_list_of_user_ids([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 9, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_is_list_of_user_ids_with_strings():
    """Call is_list_of_user_ids with list of strings."""
    try:
        result = is_list_of_user_ids(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 9, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_is_list_of_user_ids_with_mixed():
    """Call is_list_of_user_ids with mixed type list."""
    try:
        result = is_list_of_user_ids([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 9, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_is_list_of_user_ids_with_bools():
    """Call is_list_of_user_ids with list of booleans."""
    try:
        result = is_list_of_user_ids([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 9, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


def test_is_list_of_product_ids_returns_bool():
    """Verify is_list_of_product_ids returns a boolean."""
    try:
        result = is_list_of_product_ids([])
        if not isinstance(result, bool):
            BUGS.append({"line": 14, "type": "ReturnTypeMismatch", "error": f"TypeGuard is_list_of_product_ids returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 14, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_is_list_of_product_ids_with_ints():
    """Call is_list_of_product_ids with list of ints."""
    try:
        result = is_list_of_product_ids([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 14, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_is_list_of_product_ids_with_strings():
    """Call is_list_of_product_ids with list of strings."""
    try:
        result = is_list_of_product_ids(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 14, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_is_list_of_product_ids_with_mixed():
    """Call is_list_of_product_ids with mixed type list."""
    try:
        result = is_list_of_product_ids([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 14, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_is_list_of_product_ids_with_bools():
    """Call is_list_of_product_ids with list of booleans."""
    try:
        result = is_list_of_product_ids([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 14, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


def test_UserID_from_string():
    """Create UserID from a plain string."""
    try:
        val = UserID("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_UserID_from_int():
    """Create UserID from an int (wrong base type)."""
    try:
        val = UserID(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_UserID_from_none():
    """Create UserID from None."""
    try:
        val = UserID(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


def test_ProductID_from_int():
    """Create ProductID from a plain int."""
    try:
        val = ProductID(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_ProductID_from_string():
    """Create ProductID from a string (wrong base type)."""
    try:
        val = ProductID("not_an_int")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


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
