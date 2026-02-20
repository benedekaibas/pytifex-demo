# annotation: List[OrderItems]
# violation:  str instead of list


from typing import NewType, List, Tuple, TypeGuard
from typeguard import typechecked

@typechecked
def test_func() -> List[OrderItems]:
    return 'not_a_list'

test_func()
