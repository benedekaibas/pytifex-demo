"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: typealiastype-complex-nested-generics.py
Patterns detected: 1
    - main_block_replay (1 tests)
Test cases generated: 1
"""

# --- Original source ---

from typing import TypeAliasType, TypeVar, Dict, List, Tuple, Callable, Any, reveal_type, ParamSpec

K = TypeVar('K')
V = TypeVar('V')
P = ParamSpec('P')
R = TypeVar('R')

# A complex nested type involving a dictionary, list, tuple, and a generic Callable
_ComplexMetricData = Dict[K, List[Tuple[V, Callable[P, R]]]]

# TypeAliasType for this complex generic structure
ComplexMetricAlias = TypeAliasType(
    'ComplexMetricAlias',
    _ComplexMetricData,
    type_params=(K, V, P, R)
)

def process_int_metric(value: int) -> bool:
    return value > 0

def process_complex_metric_data(data: ComplexMetricAlias[str, float, [int], bool]):
    reveal_type(data) # Expected: dict[str, list[tuple[float, Callable[[int], bool]]]]
    
    first_key = next(iter(data.keys()))
    reveal_type(first_key) # Expected: str

    list_of_tuples = data[first_key]
    reveal_type(list_of_tuples) # Expected: list[tuple[float, Callable[[int], bool]]]

    first_tuple = list_of_tuples[0]
    reveal_type(first_tuple) # Expected: tuple[float, Callable[[int], bool]]

    val_from_tuple, func_from_tuple = first_tuple
    reveal_type(val_from_tuple) # Expected: float
    reveal_type(func_from_tuple) # Expected: Callable[[int], bool]
    reveal_type(func_from_tuple(5)) # Expected: bool

def test_complex_typealiastype():
    my_metrics: ComplexMetricAlias[str, float, [int], bool] = {
        "temperature": [(20.5, process_int_metric), (22.1, lambda x: x < 25)],
        "pressure": [(101.3, lambda x: x != 0)]
    }
    process_complex_metric_data(my_metrics)
    
if __name__ == "__main__":
    test_complex_typealiastype()

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_main_call_test_complex_typealiastype__():
    """Execute main block call: test_complex_typealiastype()"""
    import traceback as _tb, sys as _sys
    try:
        test_complex_typealiastype()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 46
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
