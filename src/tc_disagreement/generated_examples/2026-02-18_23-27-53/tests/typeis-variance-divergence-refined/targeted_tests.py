"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: typeis-variance-divergence-refined.py
Patterns detected: 3
    - decorator_signature (4 tests)
  - classmethod_super (2 tests)
  - main_block_replay (3 tests)
Test cases generated: 9
"""

# --- Original source ---

from typing import TypeVar, Union, reveal_type # Removed ClassVar as it's unused and kept imports minimal
from typing_extensions import TypeIs # Fixed TypeIs import from typing_extensions

T_co = TypeVar('T_co', covariant=True)

# DIVERGENCE POINT:
# Zuban (and some other stricter checkers) will raise an error here:
# "Variance of TypeVar "T_co" incompatible with variance in parent type"
# This is because `list` is an invariant generic type, but `T_co` is declared as covariant.
# Inheriting `list[T_co]` with a covariant `T_co` creates a type-unsafe situation if `MyContainer` were
# to implement methods that violate `list`'s invariance (e.g., `append`).
# Mypy, pyre, and ty often do not flag this at the class definition itself,
# but might only complain if a specific usage violates the variance.
class MyContainer(list[T_co]):
    @classmethod
    def contains_int(cls, item: object) -> TypeIs[int]:
        """Class method to check if an item is an int."""
        return isinstance(item, int)

    @classmethod
    def contains_str(cls, item: object) -> TypeIs[str]:
        """Class method to check if an item is a str."""
        return isinstance(item, str)

def process_item_with_class_method(item: Union[int, str, float]):
    if MyContainer.contains_int(item):
        reveal_type(item) # Expected: int (all checkers agree)
    elif MyContainer.contains_str(item):
        reveal_type(item) # Expected: str (all checkers agree)
    else:
        reveal_type(item) # Expected: float (all checkers agree)

if __name__ == "__main__":
    process_item_with_class_method(1)
    process_item_with_class_method("hello")
    process_item_with_class_method(3.14)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_MyContainer_contains_int_decorated_callable():
    """Verify decorated method MyContainer.contains_int is callable."""
    try:
        obj = MyContainer()
        method = getattr(obj, "contains_int", None)
        if method is None:
            BUGS.append({"line": 16, "type": "AttributeError", "error": "MyContainer has no method contains_int after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 16, "type": "TypeError", "error": "MyContainer.contains_int is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_MyContainer_contains_int_no_args():
    """Call decorated MyContainer.contains_int with no extra args."""
    try:
        obj = MyContainer()
        result = obj.contains_int()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_MyContainer_contains_str_decorated_callable():
    """Verify decorated method MyContainer.contains_str is callable."""
    try:
        obj = MyContainer()
        method = getattr(obj, "contains_str", None)
        if method is None:
            BUGS.append({"line": 21, "type": "AttributeError", "error": "MyContainer has no method contains_str after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 21, "type": "TypeError", "error": "MyContainer.contains_str is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 21, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_MyContainer_contains_str_no_args():
    """Call decorated MyContainer.contains_str with no extra args."""
    try:
        obj = MyContainer()
        result = obj.contains_str()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 21, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_MyContainer_contains_int_classmethod_call():
    """Call classmethod MyContainer.contains_int() directly."""
    try:
        result = MyContainer.contains_int()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "classmethod_call"})


def test_MyContainer_contains_str_classmethod_call():
    """Call classmethod MyContainer.contains_str() directly."""
    try:
        result = MyContainer.contains_str()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 21, "type": type(e).__name__, "error": str(e)[:200], "test": "classmethod_call"})


def test_main_call_process_item_with_class_method_1_():
    """Execute main block call: process_item_with_class_method(1)"""
    import traceback as _tb, sys as _sys
    try:
        process_item_with_class_method(1)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 34
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_process_item_with_class_method__hello__():
    """Execute main block call: process_item_with_class_method('hello')"""
    import traceback as _tb, sys as _sys
    try:
        process_item_with_class_method('hello')
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 35
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_process_item_with_class_method_3_14_():
    """Execute main block call: process_item_with_class_method(3.14)"""
    import traceback as _tb, sys as _sys
    try:
        process_item_with_class_method(3.14)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 36
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


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
