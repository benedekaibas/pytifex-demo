# annotation: None
# violation:  str instead of TypedDict


from typing import List, TypeVar, Any
from typing_extensions import TypedDict, ReadOnly
from typeguard import typechecked

@typechecked
def test_func() -> None:
    return 'not_a_dict'

test_func()
