# annotation: List[OrderItems]
# violation:  int instead of list


from typing import NewType, List, Tuple, TypeGuard
from typeguard import check_type

value = 42
check_type(value, List[OrderItems])
