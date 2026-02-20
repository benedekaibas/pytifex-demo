# annotation: None
# violation:  empty dict (missing required keys)


from typing import Protocol, List, TypedDict, runtime_checkable, Any
from typing_extensions import ReadOnly, NotRequired
from typeguard import typechecked

@typechecked
def test_func() -> None:
    return {}

test_func()
