# annotation: List[OrderItems]
# violation:  int instead of list


from typing import NewType, List, Tuple, TypeGuard
from typeguard import typechecked

@typechecked
def test_func() -> List[OrderItems]:
    return 42

test_func()
