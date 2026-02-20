# annotation: None
# violation:  empty dict (missing required keys)


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import typechecked

@typechecked
def test_func() -> None:
    return {}

test_func()
