# annotation: str
# violation:  int instead of str


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import typechecked

@typechecked
def test_func() -> str:
    return 42

test_func()
