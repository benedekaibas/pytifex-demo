"""
Hypothesis Tier 2 — Generated Property Test

Target: test_complex_typealiastype(...)
Kind: function
Line: 38
Status: PASS
Max examples: 30
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

def test_test_complex_typealiastype():
    """Test that test_complex_typealiastype() runs without type errors."""
    result = test_complex_typealiastype()


if __name__ == "__main__":
    test_test_complex_typealiastype()
