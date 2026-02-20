# annotation: Callable[Concatenate[C_cls, P_func], R_ret]
# violation:  str instead of TypedDict


from typing import TypeVar, Callable, ParamSpec, Concatenate, Any
from typing_extensions import TypedDict, ReadOnly, NotRequired
from typeguard import typechecked

@typechecked
def test_func() -> Callable[Concatenate[C_cls, P_func], R_ret]:
    return 'not_a_dict'

test_func()
