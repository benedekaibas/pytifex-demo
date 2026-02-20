# annotation: float
# violation:  None instead of float


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import typechecked

@typechecked
def test_func() -> float:
    return None

test_func()
