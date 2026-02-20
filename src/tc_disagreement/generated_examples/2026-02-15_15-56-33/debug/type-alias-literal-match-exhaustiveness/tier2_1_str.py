# annotation: str
# violation:  None instead of str


from typing import Union, TypeAlias, TypeVar, Literal, Any, Dict, List
from typeguard import typechecked

@typechecked
def test_func() -> str:
    return None

test_func()
