# annotation: bool
# violation:  str instead of bool


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import check_type

value = 'not_a_bool'
check_type(value, bool)
