"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: match-protocol-generic-type.py
Patterns detected: 1
    - protocol_conformance (7 tests)
Test cases generated: 7
"""

# --- Original source ---

import typing as t
from typing import Protocol, TypeVar, Any, Callable, Generic

P_R = TypeVar("P_R")

class Operation(Protocol[P_R]):
    def perform(self) -> P_R: ...
    def get_description(self) -> str: ...
    def default_value(self) -> P_R: ... # Method with a generic return type default behavior

class IntOp:
    def perform(self) -> int:
        return 42
    def get_description(self) -> str:
        return "Integer operation"
    def default_value(self) -> int:
        return 0

class StrOp:
    def perform(self) -> str:
        return "hello"
    def get_description(self) -> str:
        return "String operation"
    def default_value(self) -> str:
        return ""

def process_operation_result[T](op: Operation[T]) -> T:
    value = op.perform()
    
    # Type checkers might struggle to infer T correctly here when matching against value.
    # The interaction of match with a generic TypeVar that's bound by a Protocol
    # can lead to inaccurate narrowing.
    match value:
        case int() as i: # If T is int, this should match
            reveal_type(i) # Expected: int
            print(f"Matched int: {i}")
            return i 
        case str() as s: # If T is str, this should match
            reveal_type(s) # Expected: str
            print(f"Matched str: '{s}'")
            return s
        case _:
            reveal_type(value) # Expected: T (original generic type)
            print(f"Matched unexpected type: {type(value).__name__} (Value: {value}). Using default.")
            return op.default_value()

if __name__ == "__main__":
    print(f"Result for IntOp: {process_operation_result(IntOp())}")
    print(f"Result for StrOp: {process_operation_result(StrOp())}")

    class FloatOp:
        def perform(self) -> float:
            return 3.14
        def get_description(self) -> str:
            return "Float operation"
        def default_value(self) -> float:
            return 0.0
    
    print(f"Result for FloatOp: {process_operation_result(FloatOp())}")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_IntOp_has_default_value():
    """Verify IntOp has required protocol method 'default_value'."""
    try:
        obj = IntOp()
        method = getattr(obj, "default_value", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "IntOp missing protocol method default_value", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "IntOp.default_value is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_IntOp_has_perform():
    """Verify IntOp has required protocol method 'perform'."""
    try:
        obj = IntOp()
        method = getattr(obj, "perform", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "IntOp missing protocol method perform", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "IntOp.perform is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_IntOp_has_get_description():
    """Verify IntOp has required protocol method 'get_description'."""
    try:
        obj = IntOp()
        method = getattr(obj, "get_description", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "IntOp missing protocol method get_description", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "IntOp.get_description is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_StrOp_has_default_value():
    """Verify StrOp has required protocol method 'default_value'."""
    try:
        obj = StrOp()
        method = getattr(obj, "default_value", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "StrOp missing protocol method default_value", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "StrOp.default_value is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_StrOp_has_perform():
    """Verify StrOp has required protocol method 'perform'."""
    try:
        obj = StrOp()
        method = getattr(obj, "perform", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "StrOp missing protocol method perform", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "StrOp.perform is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_StrOp_has_get_description():
    """Verify StrOp has required protocol method 'get_description'."""
    try:
        obj = StrOp()
        method = getattr(obj, "get_description", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "StrOp missing protocol method get_description", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "StrOp.get_description is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_Operation_non_conforming_object():
    """Pass a non-conforming object where Protocol Operation is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


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
