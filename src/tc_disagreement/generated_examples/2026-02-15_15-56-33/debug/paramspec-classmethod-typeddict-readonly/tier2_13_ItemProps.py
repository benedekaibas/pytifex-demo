# annotation: ItemProps
# violation:  str instead of TypedDict


from typing import TypeVar, Callable, ParamSpec, Concatenate, Any
from typing_extensions import TypedDict, ReadOnly, NotRequired
from typeguard import check_type

value = 'not_a_dict'
check_type(value, ItemProps)
