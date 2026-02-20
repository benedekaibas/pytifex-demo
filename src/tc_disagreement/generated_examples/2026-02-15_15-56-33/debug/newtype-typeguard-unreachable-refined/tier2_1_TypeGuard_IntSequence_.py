# annotation: TypeGuard[IntSequence]
# violation:  str instead of TypedDict


from typing import NewType, Tuple, TypeVar, Any, TypeGuard, Union
from typeguard import typechecked

@typechecked
def test_func() -> TypeGuard[IntSequence]:
    return 'not_a_dict'

test_func()
