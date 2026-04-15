"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: dataclass-transform-classmethod-super.py
Patterns detected: 3
    - inheritance_override (4 tests)
  - decorator_signature (4 tests)
  - classmethod_super (2 tests)
Test cases generated: 10
"""

# --- Original source ---

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

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_DerivedService_get_name_via_base_ref():
    """Call DerivedService.get_name through a BaseService reference."""
    try:
        obj: BaseService = DerivedService()
        result = obj.get_name()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "override_via_base"})


def test_DerivedService_get_name_direct():
    """Call DerivedService.get_name directly."""
    try:
        obj = DerivedService()
        result = obj.get_name()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "override_direct"})


def test_DerivedService_isinstance_BaseService():
    """Verify DerivedService is an instance of BaseService."""
    try:
        obj = DerivedService()
        if not isinstance(obj, BaseService):
            BUGS.append({"line": 34, "type": "InheritanceError", "error": "DerivedService is not instance of BaseService", "test": "isinstance_check"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "isinstance_check"})


def test_DerivedService_super_get_name():
    """Verify super().get_name() works from DerivedService."""
    try:
        obj = DerivedService()
        base_method = getattr(super(type(obj), obj), "get_name", None)
        if base_method is not None:
            result = base_method()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "super_call"})


def test_BaseService_get_name_decorated_callable():
    """Verify decorated method BaseService.get_name is callable."""
    try:
        obj = BaseService()
        method = getattr(obj, "get_name", None)
        if method is None:
            BUGS.append({"line": 27, "type": "AttributeError", "error": "BaseService has no method get_name after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 27, "type": "TypeError", "error": "BaseService.get_name is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 27, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_BaseService_get_name_no_args():
    """Call decorated BaseService.get_name with no extra args."""
    try:
        obj = BaseService()
        result = obj.get_name()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 27, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_DerivedService_get_name_decorated_callable():
    """Verify decorated method DerivedService.get_name is callable."""
    try:
        obj = DerivedService()
        method = getattr(obj, "get_name", None)
        if method is None:
            BUGS.append({"line": 34, "type": "AttributeError", "error": "DerivedService has no method get_name after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 34, "type": "TypeError", "error": "DerivedService.get_name is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_DerivedService_get_name_no_args():
    """Call decorated DerivedService.get_name with no extra args."""
    try:
        obj = DerivedService()
        result = obj.get_name()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_DerivedService_get_name_classmethod_call():
    """Call classmethod DerivedService.get_name() directly."""
    try:
        result = DerivedService.get_name()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "classmethod_call"})


def test_DerivedService_get_name_matches_base_BaseService():
    """Verify DerivedService.get_name return matches BaseService.get_name."""
    try:
        derived_result = DerivedService.get_name()
        base_result = BaseService.get_name()
        if type(derived_result) != type(base_result):
            BUGS.append({"line": 34, "type": "ReturnTypeMismatch", "error": f"{type(derived_result).__name__} vs {type(base_result).__name__}", "test": "classmethod_return_type"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 34, "type": type(e).__name__, "error": str(e)[:200], "test": "classmethod_return_type"})


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
