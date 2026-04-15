"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: decorator-super-modified-signature.py
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

# A decorator that *modifies* the signature by adding a context parameter
def inject_context[**P, R](func: Callable[Concatenate[_Self, P], R]) -> Callable[Concatenate[_Self, str, P], R]:
    def wrapper(self: _Self, context: str, *args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Context: {context}")
        return func(self, *args, **kwargs)
    return wrapper

class Base:
    def process_data(self, data: int) -> str:
        return f"Base processed {data}"

class Derived(Base):
    @inject_context
    def process_data(self, context: str, data: int) -> str:
        # The original signature of super().process_data does not expect 'context'.
        # Some type checkers might struggle to understand this signature change
        # and correctly flag the call to super().
        result = super().process_data(data) # Should be error: unexpected argument for super(), or missing 'context' for self.
        return f"Derived processed with context '{context}': {result}"

if __name__ == "__main__":
    d = Derived()
    # Expecting an error here, either at definition or call site,
    # as the decorated method now requires 'context'.
    # Some checkers might not flag the 'super()' call as incorrect.
    print(d.process_data("my-context", 123))

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_Derived_process_data_via_base_ref():
    """Call Derived.process_data through a Base reference."""
    try:
        obj: Base = Derived()
        result = obj.process_data()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "override_via_base"})


def test_Derived_process_data_direct():
    """Call Derived.process_data directly."""
    try:
        obj = Derived()
        result = obj.process_data()
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


def test_Derived_super_process_data():
    """Verify super().process_data() works from Derived."""
    try:
        obj = Derived()
        base_method = getattr(super(type(obj), obj), "process_data", None)
        if base_method is not None:
            result = base_method()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "super_call"})


def test_Derived_process_data_decorated_callable():
    """Verify decorated method Derived.process_data is callable."""
    try:
        obj = Derived()
        method = getattr(obj, "process_data", None)
        if method is None:
            BUGS.append({"line": 20, "type": "AttributeError", "error": "Derived has no method process_data after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 20, "type": "TypeError", "error": "Derived.process_data is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Derived_process_data_no_args():
    """Call decorated Derived.process_data with no extra args."""
    try:
        obj = Derived()
        result = obj.process_data()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_inject_context_none_callable():
    """Call inject_context with None for Callable param 'func'."""
    try:
        inject_context(func=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_inject_context_string_callable():
    """Call inject_context with a string for Callable param 'func'."""
    try:
        inject_context(func="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_inject_context_wrong_arity_callable():
    """Call inject_context with a zero-arg callable for param 'func'."""
    try:
        inject_context(func=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


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
