# annotation: str
# violation:  int instead of str


from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type
from typeguard import check_type

value = 42
check_type(value, str)
