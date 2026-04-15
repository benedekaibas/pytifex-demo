"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: generic-closure-paramspec.py
Patterns detected: 1
    - callable_param (3 tests)
Test cases generated: 3
"""

# --- Original source ---

import typing as t
from typing import Generic, TypeVar, Callable, ParamSpec, Any

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")

def timing_decorator(func: Callable[P, R]) -> Callable[P, R]:
    """A decorator that measures execution time."""
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        import time
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"Execution of {func.__name__} took {end - start:.4f} seconds.")
        return result
    return wrapper

class DataProcessor(Generic[T]):
    def __init__(self, processing_id: str):
        self.processing_id = processing_id

    @timing_decorator
    def create_transformer(self, operation_name: str) -> Callable[[list[T]], list[T]]:
        # The closure captures 'self' (and thus 'T' and 'processing_id') and 'operation_name'.
        # Type checkers might struggle to maintain the correct type for 'T' within
        # the nested callable's signature, especially with the ParamSpec decorator
        # wrapping the outer method.
        def transformer_func(items: list[T]) -> list[T]:
            print(f"Processor '{self.processing_id}' performing '{operation_name}' on list of size {len(items)}...")
            # This line might cause issues if T's type is not correctly propagated.
            # E.g., if T is int, 'item' should be int.
            return [t.cast(T, item) for item in items if hasattr(item, '__str__')] # Dummy transformation
        return transformer_func

if __name__ == "__main__":
    str_processor = DataProcessor[str]("string_handler")
    upper_case_transformer = str_processor.create_transformer("uppercase")
    
    reveal_type(upper_case_transformer) # Expected: Callable[[list[str]], list[str]]
    
    print(upper_case_transformer(["apple", "banana", "strawberry"]))

    int_processor = DataProcessor[int]("int_handler")
    double_transformer = int_processor.create_transformer("double")
    
    reveal_type(double_transformer) # Expected: Callable[[list[int]], list[int]]
    
    print(double_transformer([1, 2, 3, 4, 5]))

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_timing_decorator_none_callable():
    """Call timing_decorator with None for Callable param 'func'."""
    try:
        timing_decorator(func=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_timing_decorator_string_callable():
    """Call timing_decorator with a string for Callable param 'func'."""
    try:
        timing_decorator(func="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_timing_decorator_wrong_arity_callable():
    """Call timing_decorator with a zero-arg callable for param 'func'."""
    try:
        timing_decorator(func=lambda: None)
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
