"""
Hypothesis Tier 2 — Generated Property Test

Target: AppConfig()
Kind: constructor
Line: 33
Status: PASS
Max examples: 30

Strategies:
  name: str -> text(max_size=30)
  version: str -> text(max_size=30)
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(name=..., version=...)
def test_AppConfig_constructor(name, version):
    """Property test: AppConfig() with generated inputs."""
    instance = AppConfig(name, version)
    assert isinstance(instance, AppConfig)


if __name__ == "__main__":
    test_AppConfig_constructor()
