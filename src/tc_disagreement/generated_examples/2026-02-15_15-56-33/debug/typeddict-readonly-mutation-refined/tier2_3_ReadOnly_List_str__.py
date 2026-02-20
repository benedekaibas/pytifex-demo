# annotation: ReadOnly[List[str]]
# violation:  str instead of TypedDict


from typing import Protocol, List, TypedDict, runtime_checkable, Any
from typing_extensions import ReadOnly, NotRequired
from typeguard import check_type

value = 'not_a_dict'
check_type(value, ReadOnly[List[str]])
