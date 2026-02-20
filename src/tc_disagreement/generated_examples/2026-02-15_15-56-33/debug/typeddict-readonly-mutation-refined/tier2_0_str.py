# annotation: str
# violation:  int instead of str


from typing import Protocol, List, TypedDict, runtime_checkable, Any
from typing_extensions import ReadOnly, NotRequired
from typeguard import check_type

value = 42
check_type(value, str)
