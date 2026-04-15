"""Hypothesis-based property test for type constraint validation.

Type annotation: bool
Test type: invalid
"""\n\n"""Hypothesis test for bool - invalid values.

Type annotation: bool
Variable: process_int_metric.__return__
Test type: invalid
"""

# Original source code
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

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, bool)
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "bool" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "bool" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
