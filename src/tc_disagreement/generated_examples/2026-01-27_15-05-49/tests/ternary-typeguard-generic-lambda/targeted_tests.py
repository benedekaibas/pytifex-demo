"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: ternary-typeguard-generic-lambda.py
Patterns detected: 2
    - typeguard_narrowing (6 tests)
  - inheritance_override (4 tests)
Test cases generated: 10
"""

# --- Original source ---

from typing import TypeVar, Union, Callable, reveal_type, TypeGuard, Any

T = TypeVar("T")

class BaseThing:
    def get_info(self) -> str:
        return "Base Info"

class SpecialThing(BaseThing):
    def get_special_info(self) -> str:
        return "Special Info"
    def get_info(self) -> str:
        return self.get_special_info()

def is_special(val: Union[T, BaseThing]) -> TypeGuard[SpecialThing]:
    """
    TypeGuard that narrows a generic type or BaseThing to SpecialThing.
    The generic T here might interact oddly with narrowing.
    """
    return isinstance(val, SpecialThing)

def process_special(s: SpecialThing) -> str:
    return s.get_special_info()

def get_action_lambda(x: Union[T, BaseThing, None]) -> Callable[[], Union[str, None]]:
    # The core test: ternary operator's condition uses TypeGuard, and branches return lambdas
    # that capture `x`. The narrowing of `x` must correctly apply *inside* the lambda.
    action_lambda: Callable[[], Union[str, None]] = (
        (lambda: process_special(x)) if is_special(x) else (lambda: None)
    )
    
    reveal_type(action_lambda) # Expected: Callable[[], Union[str, None]]
    
    # Test the return type of the lambda call
    lambda_result = action_lambda()
    reveal_type(lambda_result) # Expected: Union[str, None]

    return action_lambda

if __name__ == "__main__":
    special_obj = SpecialThing()
    base_obj = BaseThing()
    none_obj = None

    lambda_s = get_action_lambda(special_obj)
    print(f"Special lambda result: {lambda_s()}") # Expected: Special Info
    
    lambda_b = get_action_lambda(base_obj)
    print(f"Base lambda result: {lambda_b()}") # Expected: None
    
    lambda_n = get_action_lambda(none_obj)
    print(f"None lambda result: {lambda_n()}") # Expected: None

    print("\nExample demonstrating TypeGuard narrowing within a lambda chosen by a ternary expression.")
    print("Checks if type checkers correctly narrow the captured variable `x` for the `process_special(x)` call.")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_is_special_returns_bool():
    """Verify is_special returns a boolean."""
    try:
        result = is_special([])
        if not isinstance(result, bool):
            BUGS.append({"line": 15, "type": "ReturnTypeMismatch", "error": f"TypeGuard is_special returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 15, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_is_special_with_none():
    """Call is_special with None."""
    try:
        is_special(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 15, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_none"})


def test_is_special_with_ints():
    """Call is_special with list of ints."""
    try:
        result = is_special([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 15, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_is_special_with_strings():
    """Call is_special with list of strings."""
    try:
        result = is_special(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 15, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_is_special_with_mixed():
    """Call is_special with mixed type list."""
    try:
        result = is_special([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 15, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_is_special_with_bools():
    """Call is_special with list of booleans."""
    try:
        result = is_special([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 15, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


def test_SpecialThing_get_info_via_base_ref():
    """Call SpecialThing.get_info through a BaseThing reference."""
    try:
        obj: BaseThing = SpecialThing()
        result = obj.get_info()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 12, "type": type(e).__name__, "error": str(e)[:200], "test": "override_via_base"})


def test_SpecialThing_get_info_direct():
    """Call SpecialThing.get_info directly."""
    try:
        obj = SpecialThing()
        result = obj.get_info()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 12, "type": type(e).__name__, "error": str(e)[:200], "test": "override_direct"})


def test_SpecialThing_isinstance_BaseThing():
    """Verify SpecialThing is an instance of BaseThing."""
    try:
        obj = SpecialThing()
        if not isinstance(obj, BaseThing):
            BUGS.append({"line": 12, "type": "InheritanceError", "error": "SpecialThing is not instance of BaseThing", "test": "isinstance_check"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 12, "type": type(e).__name__, "error": str(e)[:200], "test": "isinstance_check"})


def test_SpecialThing_super_get_info():
    """Verify super().get_info() works from SpecialThing."""
    try:
        obj = SpecialThing()
        base_method = getattr(super(type(obj), obj), "get_info", None)
        if base_method is not None:
            result = base_method()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 12, "type": type(e).__name__, "error": str(e)[:200], "test": "super_call"})


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
