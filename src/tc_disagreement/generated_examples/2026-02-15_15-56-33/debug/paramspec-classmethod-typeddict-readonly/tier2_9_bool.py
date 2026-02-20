# annotation: bool
# violation:  str instead of bool


from typing import TypeVar, Callable, ParamSpec, Concatenate, Any
from typing_extensions import TypedDict, ReadOnly, NotRequired
from typeguard import typechecked

@typechecked
def test_func() -> bool:
    return 'not_a_bool'

test_func()
