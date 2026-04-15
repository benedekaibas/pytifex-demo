"""
Hypothesis Tier 2 — Generated Test

Call: CustomInitData(value='test')
Kind: constructor
Line: 43
Status: FAIL

Bug: [TypeError] CustomInitData(value='test') -> TypeError: object.__init__() takes exactly one argument (the instance to initialize)
"""

# --- Original source (full context) ---

from collections.abc import Callable
from typing import TypeVar, ParamSpec, Concatenate, Any, dataclass_transform
from dataclasses import dataclass, field

_P = ParamSpec("_P")
_R = TypeVar("_R")
_T = TypeVar("_T", bound=type)

# A factory for a decorator that preserves signature using ParamSpec
@dataclass_transform(kw_only_default=True)
def class_builder[T: type](*, frozen: bool = False, extra_init: bool = False) -> Callable[[T], T]:
    def wrapper(cls: T) -> T:
        # We can simulate adding an __init__ if extra_init is True
        if extra_init:
            original_init = getattr(cls, '__init__', None)
            def new_init(self, *args, **kwargs):
                print(f"Custom init for {cls.__name__}")
                if original_init:
                    original_init(self, *args, **kwargs)
            cls.__init__ = new_init # type: ignore
        return dataclass(frozen=frozen)(cls)
    return wrapper

@class_builder(frozen=True)
class ImmutableData:
    id: int
    name: str = "default"

@class_builder(extra_init=True)
class CustomInitData:
    value: str
    counter: int = field(default=0)

if __name__ == "__main__":
    # This should work fine and be correctly typed.
    # The issue might arise if the type checker struggles to apply
    # dataclass_transform semantics when the returned callable has a complex
    # ParamSpec signature (even though here it's T -> T, it's about the wrapper's internals).
    data1 = ImmutableData(id=1, name="first")
    print(data1.id, data1.name)
    # reveal_type(data1)

    data2 = CustomInitData(value="test")
    print(data2.value, data2.counter)
    # reveal_type(data2)

    # Some checkers might fail to recognize 'id' and 'name' as constructor arguments,
    # or fail to infer the frozen/default behavior.
    # data_bad = ImmutableData(id=1, unexpected="foo") # Should be error
    # data_missing = ImmutableData() # Should be error (id is missing)


# --- Tier 2 test ---

def test_CustomInitData_constructor():
    """Test that CustomInitData() can be constructed."""
    try:
        instance = CustomInitData(value='test')
        print(f"OK: {instance}")
    except (TypeError, AttributeError, ValueError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_CustomInitData_constructor()
