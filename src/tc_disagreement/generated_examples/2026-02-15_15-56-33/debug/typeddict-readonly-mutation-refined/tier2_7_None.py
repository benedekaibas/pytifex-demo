# annotation: None
# violation:  str instead of TypedDict


from typing import Protocol, List, TypedDict, runtime_checkable, Any
from typing_extensions import ReadOnly, NotRequired
from typeguard import typechecked

@typechecked
def test_func() -> None:
    return 'not_a_dict'

test_func()
