# annotation: float
# violation:  str instead of float


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import typechecked

@typechecked
def test_func() -> float:
    return 'not_a_float'

test_func()
