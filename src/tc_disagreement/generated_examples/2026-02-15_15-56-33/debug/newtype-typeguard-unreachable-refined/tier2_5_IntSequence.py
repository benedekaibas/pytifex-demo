# annotation: IntSequence
# violation:  str instead of TypedDict


from typing import NewType, Tuple, TypeVar, Any, TypeGuard, Union
from typeguard import check_type

value = 'not_a_dict'
check_type(value, IntSequence)
