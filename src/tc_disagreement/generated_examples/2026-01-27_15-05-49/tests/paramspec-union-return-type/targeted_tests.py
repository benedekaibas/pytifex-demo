"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: paramspec-union-return-type.py
Patterns detected: 1
    - callable_param (3 tests)
Test cases generated: 3
"""

# --- Original source ---

from typing import TypeVar, ParamSpec, Callable, Union, reveal_type, Type

P = ParamSpec("P")
R = TypeVar("R")

def conditional_decorator(
    func: Callable[P, R]
) -> Union[Callable[P, R], Callable[P, Type[None]]]:
    """
    A decorator that *type-system-wise* implies it might return a callable with the original return type,
    or one whose return type is `Type[None]`. At runtime, it always returns the original.
    This tests ParamSpec resolution within a Union return.
    """
    class OriginalWrapper:
        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
            print(f"Calling {func.__name__} with original return type")
            return func(*args, **kwargs)

    class AltWrapper:
        def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Type[None]:
            print(f"Calling {func.__name__} with Type[None] return type (should not happen at runtime)")
            func(*args, **kwargs)
            return type(None) # Always returns the type object None

    # This branch is never taken at runtime, but affects the static type.
    if False:
        return AltWrapper()
    else:
        return OriginalWrapper()

def my_function(x: int, y: str) -> float:
    return float(x) + len(y)

decorated_func = conditional_decorator(my_function)

# Type checker should infer decorated_func as Union[Callable[[int, str], float], Callable[[int, str], Type[None]]]
reveal_type(decorated_func)

# The result of calling decorated_func should reflect the Union of return types.
result = decorated_func(10, "hello")
reveal_type(result) # Expected: Union[float, Type[None]]

if __name__ == "__main__":
    print(f"Result from calling decorated_func: {decorated_func(1, 'world')}")
    # At runtime, it will always be a float, but type checkers should respect the annotation.

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_conditional_decorator_none_callable():
    """Call conditional_decorator with None for Callable param 'func'."""
    try:
        conditional_decorator(func=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_conditional_decorator_string_callable():
    """Call conditional_decorator with a string for Callable param 'func'."""
    try:
        conditional_decorator(func="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_conditional_decorator_wrong_arity_callable():
    """Call conditional_decorator with a zero-arg callable for param 'func'."""
    try:
        conditional_decorator(func=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


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
