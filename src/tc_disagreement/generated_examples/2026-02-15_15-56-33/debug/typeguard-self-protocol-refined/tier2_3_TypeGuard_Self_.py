# annotation: TypeGuard[Self]
# violation:  str instead of TypedDict


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import typechecked

@typechecked
def test_func() -> TypeGuard[Self]:
    return 'not_a_dict'

test_func()
