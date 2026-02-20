# annotation: Tuple[int, ...]
# violation:  empty dict (missing required keys)


from typing import NewType, Tuple, TypeVar, Any, TypeGuard, Union
from typeguard import check_type

value = {}
check_type(value, Tuple[int, ...])
