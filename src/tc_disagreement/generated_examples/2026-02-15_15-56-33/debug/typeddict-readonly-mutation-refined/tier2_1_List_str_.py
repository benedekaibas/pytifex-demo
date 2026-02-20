# annotation: List[str]
# violation:  str instead of list


from typing import Protocol, List, TypedDict, runtime_checkable, Any
from typing_extensions import ReadOnly, NotRequired
from typeguard import check_type

value = 'not_a_list'
check_type(value, List[str])
