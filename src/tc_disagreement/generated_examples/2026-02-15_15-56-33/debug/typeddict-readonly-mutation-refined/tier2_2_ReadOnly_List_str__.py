# annotation: ReadOnly[List[str]]
# violation:  empty dict (missing required keys)


from typing import Protocol, List, TypedDict, runtime_checkable, Any
from typing_extensions import ReadOnly, NotRequired
from typeguard import check_type

value = {}
check_type(value, ReadOnly[List[str]])
