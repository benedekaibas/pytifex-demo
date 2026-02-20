# annotation: str
# violation:  int instead of str


from typing import TypeVar, Callable, ParamSpec, Concatenate, Any
from typing_extensions import TypedDict, ReadOnly, NotRequired
from typeguard import check_type

value = 42
check_type(value, str)
