"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: classvar-protocol-self.py
Patterns detected: 3
    - decorator_signature (2 tests)
  - protocol_conformance (3 tests)
  - classmethod_super (1 tests)
Test cases generated: 6
"""

# --- Original source ---

import typing as t
from typing import ClassVar, Protocol, Self, Dict, Any

class Configurable(Protocol):
    _config_cache: ClassVar[Dict[str, Any]] = {} # Protocol can define defaults
    _is_config_loaded: ClassVar[bool] = False

    @classmethod
    def load_config(cls) -> None: ...

    def get_setting(self, key: str) -> Any: ...

class MyConfigLoader:
    _config_cache: ClassVar[Dict[str, Any]] = {}
    _is_config_loaded: ClassVar[bool] = False

    @classmethod
    def load_config(cls) -> None:
        if not cls._is_config_loaded:
            print("Loading configuration...")
            cls._config_cache = {"timeout": 30, "retries": 5, "feature_x_enabled": True}
            cls._is_config_loaded = True

    def get_setting(self: Self, key: str) -> Any:
        # Accessing ClassVar via Self might cause disagreement.
        # Type checkers need to resolve Self to MyConfigLoader and then access the ClassVar.
        # This can be problematic if Self is treated as an instance with a non-dict attribute.
        if not self._config_cache: # Type checker might incorrectly infer self._config_cache as Self or MyConfigLoader
            self.load_config() # Ensure config is loaded via classmethod
        
        if key not in self._config_cache:
            raise KeyError(f"Setting '{key}' not found.")
        
        reveal_type(self._config_cache) # Expected: Dict[str, Any]
        return self._config_cache[key]

if __name__ == "__main__":
    loader = MyConfigLoader()
    print(f"Timeout setting: {loader.get_setting('timeout')}")
    print(f"Retries setting: {loader.get_setting('retries')}")
    
    loader2 = MyConfigLoader()
    print(f"Feature X enabled: {loader2.get_setting('feature_x_enabled')}")
    
    # Test setting that doesn't exist
    try:
        loader.get_setting('non_existent_setting')
    except KeyError as e:
        print(e)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_MyConfigLoader_load_config_decorated_callable():
    """Verify decorated method MyConfigLoader.load_config is callable."""
    try:
        obj = MyConfigLoader()
        method = getattr(obj, "load_config", None)
        if method is None:
            BUGS.append({"line": 18, "type": "AttributeError", "error": "MyConfigLoader has no method load_config after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 18, "type": "TypeError", "error": "MyConfigLoader.load_config is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_MyConfigLoader_load_config_no_args():
    """Call decorated MyConfigLoader.load_config with no extra args."""
    try:
        obj = MyConfigLoader()
        result = obj.load_config()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_MyConfigLoader_has_load_config():
    """Verify MyConfigLoader has required protocol method 'load_config'."""
    try:
        obj = MyConfigLoader()
        method = getattr(obj, "load_config", None)
        if method is None:
            BUGS.append({"line": 4, "type": "AttributeError", "error": "MyConfigLoader missing protocol method load_config", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 4, "type": "TypeError", "error": "MyConfigLoader.load_config is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_MyConfigLoader_has_get_setting():
    """Verify MyConfigLoader has required protocol method 'get_setting'."""
    try:
        obj = MyConfigLoader()
        method = getattr(obj, "get_setting", None)
        if method is None:
            BUGS.append({"line": 4, "type": "AttributeError", "error": "MyConfigLoader missing protocol method get_setting", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 4, "type": "TypeError", "error": "MyConfigLoader.get_setting is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_Configurable_non_conforming_object():
    """Pass a non-conforming object where Protocol Configurable is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


def test_Configurable_load_config_classmethod_call():
    """Call classmethod Configurable.load_config() directly."""
    try:
        result = Configurable.load_config()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 9, "type": type(e).__name__, "error": str(e)[:200], "test": "classmethod_call"})


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
