"""
Hypothesis Tier 2 — Generated Property Test

Target: MyConfigLoader.get_setting(...)
Kind: method
Line: 24
Status: PASS
Max examples: 30

Strategies:
  key: str -> text(max_size=30)
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(receiver=..., key=...)
def test_MyConfigLoader_get_setting(receiver, key):
    """Property test: MyConfigLoader.get_setting() with generated inputs."""
    result = receiver.get_setting(key)
    # Expected return type: Any


if __name__ == "__main__":
    test_MyConfigLoader_get_setting()
