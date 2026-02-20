# annotation: TypeGuard[OrderItems]
# violation:  empty dict (missing required keys)


from typing import NewType, List, Tuple, TypeGuard
from typeguard import typechecked

@typechecked
def test_func() -> TypeGuard[OrderItems]:
    return {}

test_func()
