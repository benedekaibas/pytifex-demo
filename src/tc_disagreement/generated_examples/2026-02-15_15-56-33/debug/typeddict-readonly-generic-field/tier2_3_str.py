# annotation: str
# violation:  int instead of str


from typing import List, TypeVar, Any
from typing_extensions import TypedDict, ReadOnly
from typeguard import check_type

value = 42
check_type(value, str)
