# annotation: int
# violation:  str instead of int


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import check_type

value = 'not_an_int'
check_type(value, int)
