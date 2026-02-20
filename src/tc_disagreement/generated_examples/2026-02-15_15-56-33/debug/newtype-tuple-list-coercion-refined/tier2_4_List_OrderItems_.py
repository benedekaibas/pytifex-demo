# annotation: List[OrderItems]
# violation:  str instead of list


from typing import NewType, List, Tuple, TypeGuard
from typeguard import check_type

value = 'not_a_list'
check_type(value, List[OrderItems])
