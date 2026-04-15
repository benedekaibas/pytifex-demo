"""
Hypothesis Tier 2 — Generated Property Test

Target: BaseService.get_name(...)
Kind: function
Line: 27
Status: PASS
Max examples: 30
"""

# --- Original source (full context) ---

from collections.abc import Callable
from typing import TypeVar, ParamSpec, Concatenate, Any, dataclass_transform, ClassVar
from dataclasses import dataclass

_P = ParamSpec("_P")
_R = TypeVar("_R")
_Cls = TypeVar("_Cls", bound=type)

# A custom decorator factory designed for class methods.
# It simulates `dataclass_transform`'s effect on a class method
# potentially altering its signature or behavior.
def method_config[T: type](*, log_calls: bool = False) -> Callable[[T], T]:
    def wrap_class_method_factory(cls: T) -> T:
        for name, method in cls.__dict__.items():
            if isinstance(method, classmethod):
                original_func = method.__wrapped__ # type: ignore
                if log_calls:
                    def logged_classmethod(cls_obj: Any, *args: _P.args, **kwargs: _P.kwargs) -> Any:
                        print(f"LOG: Calling class method {cls.__name__}.{original_func.__name__}")
                        return original_func(cls_obj, *args, **kwargs)
                    setattr(cls, name, classmethod(logged_classmethod)) # type: ignore
        return cls
    return wrap_class_method_factory

class BaseService:
    @classmethod
    def get_name(cls) -> str:
        return "BaseService"

class DerivedService(BaseService):
    # Apply a "dataclass_transform-like" decorator to a class method
    @method_config(log_calls=True)
    @classmethod
    def get_name(cls) -> str:
        # Calling super() on a decorated class method can be tricky.
        # The decorator might change the signature *at runtime* or create a wrapper
        # that type checkers struggle to understand in relation to super().
        return f"Derived({super().get_name()})" # Some checkers might flag super().get_name()

if __name__ == "__main__":
    print(BaseService.get_name())
    print(DerivedService.get_name())

    # Checkers might incorrectly infer the type of DerivedService.get_name
    # or flag the super() call within it, especially if the decorator
    # is complex or uses ParamSpec in a way that interferes.
    # reveal_type(DerivedService.get_name)


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

def test_BaseService_get_name():
    """Test that BaseService.get_name() runs without type errors."""
    result = BaseService.get_name()


if __name__ == "__main__":
    test_BaseService_get_name()
