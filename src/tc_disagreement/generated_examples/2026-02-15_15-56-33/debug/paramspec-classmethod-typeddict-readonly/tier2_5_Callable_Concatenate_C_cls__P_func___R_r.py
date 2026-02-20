# annotation: Callable[Concatenate[C_cls, P_func], R_ret]
# violation:  empty dict (missing required keys)


from typing import TypeVar, Callable, ParamSpec, Concatenate, Any
from typing_extensions import TypedDict, ReadOnly, NotRequired
from typeguard import typechecked

@typechecked
def test_func() -> Callable[Concatenate[C_cls, P_func], R_ret]:
    return {}

test_func()
