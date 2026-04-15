"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: dataclass-transform-protocol-default-methods.py
Patterns detected: 3
    - inheritance_override (4 tests)
  - decorator_signature (1 tests)
  - protocol_conformance (4 tests)
Test cases generated: 9
"""

# --- Original source ---

from collections.abc import Callable
from typing import Protocol, TypeVar, dataclass_transform
from dataclasses import dataclass

T = TypeVar("T")

class BaseConfig(Protocol):
    # Protocol method with a default implementation
    # This makes it harder for dataclass_transform to infer if it should
    # generate an __init__ for this or respect the default.
    def is_valid(self) -> bool:
        return True # Default implementation

    def get_setting(self, key: str) -> str:
        return "default_setting"

@dataclass_transform()
def config_factory[T: type](*, cache: bool = False) -> Callable[[T], T]:
    def wrapper(cls: T) -> T:
        # Potentially, this wrapper could modify or replace methods
        # defined in the protocol, leading to conflicts.
        if cache:
            # Add a caching mechanism, e.g., for get_setting
            original_get_setting = getattr(cls, 'get_setting', None)
            def cached_get_setting(self, key: str) -> str:
                # Simplistic cache
                return original_get_setting(self, key) if original_get_setting else super(cls, self).get_setting(key) # type: ignore
            cls.get_setting = cached_get_setting # type: ignore
        return dataclass(frozen=False)(cls)
    return wrapper

@config_factory(cache=True)
class AppConfig(BaseConfig):
    name: str
    version: str

    # Explicitly override a method that has a default in the protocol
    def is_valid(self) -> bool:
        return self.name != "" and self.version != ""

    # No override for get_setting, should use protocol default or decorated version
    # def get_setting(self, key: str) -> str:
    #     return f"AppConfig specific {key}"

if __name__ == "__main__":
    app_cfg = AppConfig(name="MyApp", version="1.0")
    print(f"Config name: {app_cfg.name}, version: {app_cfg.version}")
    print(f"Is valid: {app_cfg.is_valid()}") # Should call AppConfig's method
    print(f"Get setting 'theme': {app_cfg.get_setting('theme')}") # Should call decorated or protocol's default

    # Type checkers might disagree on:
    # 1. Whether AppConfig correctly implements BaseConfig due to the dataclass_transform.
    # 2. The callable signature of AppConfig's constructor.
    # 3. The actual implementation called for get_setting.
    # reveal_type(app_cfg.is_valid)
    # reveal_type(app_cfg.get_setting)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_AppConfig_is_valid_via_base_ref():
    """Call AppConfig.is_valid through a BaseConfig reference."""
    try:
        obj: BaseConfig = AppConfig()
        result = obj.is_valid()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 38, "type": type(e).__name__, "error": str(e)[:200], "test": "override_via_base"})


def test_AppConfig_is_valid_direct():
    """Call AppConfig.is_valid directly."""
    try:
        obj = AppConfig()
        result = obj.is_valid()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 38, "type": type(e).__name__, "error": str(e)[:200], "test": "override_direct"})


def test_AppConfig_isinstance_BaseConfig():
    """Verify AppConfig is an instance of BaseConfig."""
    try:
        obj = AppConfig()
        if not isinstance(obj, BaseConfig):
            BUGS.append({"line": 38, "type": "InheritanceError", "error": "AppConfig is not instance of BaseConfig", "test": "isinstance_check"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 38, "type": type(e).__name__, "error": str(e)[:200], "test": "isinstance_check"})


def test_AppConfig_super_is_valid():
    """Verify super().is_valid() works from AppConfig."""
    try:
        obj = AppConfig()
        base_method = getattr(super(type(obj), obj), "is_valid", None)
        if base_method is not None:
            result = base_method()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 38, "type": type(e).__name__, "error": str(e)[:200], "test": "super_call"})


def test_config_factory_decorated_callable():
    """Verify decorated function config_factory is callable."""
    if not callable(config_factory):
        BUGS.append({"line": 18, "type": "TypeError", "error": "config_factory is not callable after decoration", "test": "decorated_callable"})


def test_AppConfig_has_get_setting():
    """Verify AppConfig has required protocol method 'get_setting'."""
    try:
        obj = AppConfig()
        method = getattr(obj, "get_setting", None)
        if method is None:
            BUGS.append({"line": 7, "type": "AttributeError", "error": "AppConfig missing protocol method get_setting", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 7, "type": "TypeError", "error": "AppConfig.get_setting is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_AppConfig_has_is_valid():
    """Verify AppConfig has required protocol method 'is_valid'."""
    try:
        obj = AppConfig()
        method = getattr(obj, "is_valid", None)
        if method is None:
            BUGS.append({"line": 7, "type": "AttributeError", "error": "AppConfig missing protocol method is_valid", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 7, "type": "TypeError", "error": "AppConfig.is_valid is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_BaseConfig_non_conforming_object():
    """Pass a non-conforming object where Protocol BaseConfig is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


def test_AppConfig_non_conforming_object():
    """Pass a non-conforming object where Protocol AppConfig is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


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
