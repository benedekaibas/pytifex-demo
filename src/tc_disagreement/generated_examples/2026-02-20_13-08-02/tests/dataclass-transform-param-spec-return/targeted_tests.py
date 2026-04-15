"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: dataclass-transform-param-spec-return.py
Patterns detected: 1
    - decorator_signature (1 tests)
Test cases generated: 1
"""

# --- Original source ---

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

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_class_builder_decorated_callable():
    """Verify decorated function class_builder is callable."""
    if not callable(class_builder):
        BUGS.append({"line": 11, "type": "TypeError", "error": "class_builder is not callable after decoration", "test": "decorated_callable"})


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
