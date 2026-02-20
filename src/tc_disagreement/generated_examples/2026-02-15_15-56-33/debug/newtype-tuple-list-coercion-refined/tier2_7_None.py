# annotation: None
# violation:  str instead of TypedDict


from typing import NewType, List, Tuple, TypeGuard
from typeguard import typechecked

@typechecked
def test_func() -> None:
    return 'not_a_dict'

test_func()
