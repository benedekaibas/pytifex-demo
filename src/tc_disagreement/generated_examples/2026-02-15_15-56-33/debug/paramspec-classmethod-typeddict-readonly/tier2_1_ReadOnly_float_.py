# annotation: ReadOnly[float]
# violation:  empty dict (missing required keys)


from typing import TypeVar, Callable, ParamSpec, Concatenate, Any
from typing_extensions import TypedDict, ReadOnly, NotRequired
from typeguard import check_type

value = {}
check_type(value, ReadOnly[float])
