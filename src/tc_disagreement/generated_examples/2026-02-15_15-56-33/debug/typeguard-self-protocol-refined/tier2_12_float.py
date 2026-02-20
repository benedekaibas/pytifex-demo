# annotation: float
# violation:  str instead of float


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import check_type

value = 'not_a_float'
check_type(value, float)
