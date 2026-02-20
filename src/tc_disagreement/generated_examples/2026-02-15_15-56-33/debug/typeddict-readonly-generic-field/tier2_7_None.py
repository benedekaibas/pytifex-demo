# annotation: None
# violation:  empty dict (missing required keys)


from typing import List, TypeVar, Any
from typing_extensions import TypedDict, ReadOnly
from typeguard import typechecked

@typechecked
def test_func() -> None:
    return {}

test_func()
