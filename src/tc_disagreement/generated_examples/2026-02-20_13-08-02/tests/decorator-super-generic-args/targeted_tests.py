"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: decorator-super-generic-args.py
Patterns detected: 3
    - inheritance_override (4 tests)
  - decorator_signature (2 tests)
  - callable_param (3 tests)
Test cases generated: 9
"""

# --- Original source ---

from typing import Any, TypeVar, Callable, ParamSpec, Concatenate

_R = TypeVar("_R")
_P = ParamSpec("_P")
_Self = TypeVar("_Self")

def trace_method[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """A decorator that logs calls but preserves the signature."""
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__qualname__} with args: {args}, kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class Base:
    def greet(self, name: str) -> str:
        return f"Hello, {name} from Base!"

class Derived(Base):
    @trace_method
    def greet(self, name: str) -> str:
        # Some type checkers might incorrectly flag this as missing arguments
        # for super().greet(), despite ParamSpec preserving the signature.
        return super().greet(name)

if __name__ == "__main__":
    d = Derived()
    print(d.greet("World"))

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_Derived_greet_via_base_ref():
    """Call Derived.greet through a Base reference."""
    try:
        obj: Base = Derived()
        result = obj.greet()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "override_via_base"})


def test_Derived_greet_direct():
    """Call Derived.greet directly."""
    try:
        obj = Derived()
        result = obj.greet()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "override_direct"})


def test_Derived_isinstance_Base():
    """Verify Derived is an instance of Base."""
    try:
        obj = Derived()
        if not isinstance(obj, Base):
            BUGS.append({"line": 20, "type": "InheritanceError", "error": "Derived is not instance of Base", "test": "isinstance_check"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "isinstance_check"})


def test_Derived_super_greet():
    """Verify super().greet() works from Derived."""
    try:
        obj = Derived()
        base_method = getattr(super(type(obj), obj), "greet", None)
        if base_method is not None:
            result = base_method()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "super_call"})


def test_Derived_greet_decorated_callable():
    """Verify decorated method Derived.greet is callable."""
    try:
        obj = Derived()
        method = getattr(obj, "greet", None)
        if method is None:
            BUGS.append({"line": 20, "type": "AttributeError", "error": "Derived has no method greet after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 20, "type": "TypeError", "error": "Derived.greet is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Derived_greet_no_args():
    """Call decorated Derived.greet with no extra args."""
    try:
        obj = Derived()
        result = obj.greet()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_trace_method_none_callable():
    """Call trace_method with None for Callable param 'func'."""
    try:
        trace_method(func=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_trace_method_string_callable():
    """Call trace_method with a string for Callable param 'func'."""
    try:
        trace_method(func="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_trace_method_wrong_arity_callable():
    """Call trace_method with a zero-arg callable for param 'func'."""
    try:
        trace_method(func=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


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
