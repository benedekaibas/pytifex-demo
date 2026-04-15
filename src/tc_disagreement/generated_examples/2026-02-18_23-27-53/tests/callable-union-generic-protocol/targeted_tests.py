"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: callable-union-generic-protocol.py
Patterns detected: 3
    - callable_param (3 tests)
  - protocol_conformance (3 tests)
  - main_block_replay (2 tests)
Test cases generated: 8
"""

# --- Original source ---

from typing import Protocol, TypeVar, Callable, Any, Union, reveal_type, runtime_checkable

T = TypeVar('T')

@runtime_checkable
class Converter(Protocol[T]):
    def __call__(self, arg: Any) -> T: ...
    def convert_default(self) -> T: ...

class IntConverter:
    def __call__(self, arg: Any) -> int:
        return int(arg)
    def convert_default(self) -> int:
        return 0

def handle_mixed_callable(cb: Callable[..., Any] | Converter[str] | None):
    if callable(cb):
        # Type checkers might disagree on the materialization of this union.
        # Some might simplify to Callable[..., Any], others might keep the union.
        reveal_type(cb) # Expected: Callable[..., Any] | Converter[str]

        # Call with arguments expected by Callable[..., Any]
        result_any = cb(1, "test", kw=True)
        reveal_type(result_any) # Expected: Any (if Callable[..., Any] dominates)

        if isinstance(cb, Converter):
            reveal_type(cb) # Expected: Converter[str]
            converted_str = cb("hello")
            reveal_type(converted_str) # Expected: str
            default_str = cb.convert_default()
            reveal_type(default_str) # Expected: str
        else:
            reveal_type(cb) # Expected: Callable[..., Any] (after excluding Converter)
            result_simple = cb(10)
            reveal_type(result_simple) # Expected: Any
    else:
        reveal_type(cb) # Expected: None

if __name__ == "__main__":
    handle_mixed_callable(IntConverter()) # Should satisfy Callable[..., Any] for call, but not Converter[str]
    handle_mixed_callable(lambda x: str(x)) # Should satisfy Callable[..., Any]
    handle_mixed_callable(None)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_handle_mixed_callable_none_callable():
    """Call handle_mixed_callable with None for Callable param 'cb'."""
    try:
        handle_mixed_callable(cb=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_handle_mixed_callable_string_callable():
    """Call handle_mixed_callable with a string for Callable param 'cb'."""
    try:
        handle_mixed_callable(cb="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_handle_mixed_callable_wrong_arity_callable():
    """Call handle_mixed_callable with a zero-arg callable for param 'cb'."""
    try:
        handle_mixed_callable(cb=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


def test_IntConverter_has___call__():
    """Verify IntConverter has required protocol method '__call__'."""
    try:
        obj = IntConverter()
        method = getattr(obj, "__call__", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "IntConverter missing protocol method __call__", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "IntConverter.__call__ is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_IntConverter_has_convert_default():
    """Verify IntConverter has required protocol method 'convert_default'."""
    try:
        obj = IntConverter()
        method = getattr(obj, "convert_default", None)
        if method is None:
            BUGS.append({"line": 6, "type": "AttributeError", "error": "IntConverter missing protocol method convert_default", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 6, "type": "TypeError", "error": "IntConverter.convert_default is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_Converter_non_conforming_object():
    """Pass a non-conforming object where Protocol Converter is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


def test_main_call_handle_mixed_callable_IntConverter___():
    """Execute main block call: handle_mixed_callable(IntConverter())"""
    import traceback as _tb, sys as _sys
    try:
        handle_mixed_callable(IntConverter())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 40
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_handle_mixed_callable_None_():
    """Execute main block call: handle_mixed_callable(None)"""
    import traceback as _tb, sys as _sys
    try:
        handle_mixed_callable(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 42
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
