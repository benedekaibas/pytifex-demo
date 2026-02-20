# annotation: TypeGuard[IntSequence]
# violation:  empty dict (missing required keys)


from typing import NewType, Tuple, TypeVar, Any, TypeGuard, Union
from typeguard import typechecked

@typechecked
def test_func() -> TypeGuard[IntSequence]:
    return {}

test_func()
