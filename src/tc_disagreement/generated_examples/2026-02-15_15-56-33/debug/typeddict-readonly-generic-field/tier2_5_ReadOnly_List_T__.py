# annotation: ReadOnly[List[T]]
# violation:  str instead of TypedDict


from typing import List, TypeVar, Any
from typing_extensions import TypedDict, ReadOnly
from typeguard import check_type

value = 'not_a_dict'
check_type(value, ReadOnly[List[T]])
