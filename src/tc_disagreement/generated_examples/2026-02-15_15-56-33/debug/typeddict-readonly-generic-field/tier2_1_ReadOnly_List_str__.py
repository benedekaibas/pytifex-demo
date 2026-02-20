# annotation: ReadOnly[List[str]]
# violation:  empty dict (missing required keys)


from typing import List, TypeVar, Any
from typing_extensions import TypedDict, ReadOnly
from typeguard import check_type

value = {}
check_type(value, ReadOnly[List[str]])
