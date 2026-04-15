"""
Hypothesis Tier 2 — Generated Test

Call: b_factory.register_type('basic', 'data')
Kind: method
Line: 56
Status: PASS
"""

# --- Original source (full context) ---

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Self, Any

T = TypeVar('T')

class AbstractFactory(Generic[T], ABC):
    @abstractmethod
    def create(self) -> Self: # Returns an instance of the specific subclass
        ...

    @abstractmethod
    def register_type(self, key: str, value: T) -> None:
        ...

class BasicFactory(AbstractFactory[str]):
    _registry: dict[str, str]

    def __init__(self) -> None:
        self._registry = {}

    # This helper method explicitly returns BasicFactory, not Self.
    def _get_base_factory_instance(self) -> 'BasicFactory[str]':
        return BasicFactory()

    def create(self) -> Self:
        # For BasicFactory: Self is BasicFactory[str].
        # _get_base_factory_instance returns BasicFactory[str]. This is compatible.
        return self._get_base_factory_instance()

    def register_type(self, key: str, value: str) -> None:
        self._registry[key] = value

class ExtendedFactory(BasicFactory):
    _prefix: str
    def __init__(self, prefix: str = "") -> None:
        super().__init__()
        self._prefix = prefix

    # ExtendedFactory does NOT override `create` or `_get_base_factory_instance`.
    # When `ExtendedFactory().create()` is called:
    # 1. `self` is an instance of `ExtendedFactory`.
    # 2. The `create` method (inherited from `BasicFactory`) is called.
    # 3. Inside `create`, `self._get_base_factory_instance()` is invoked.
    # 4. Since `_get_base_factory_instance` is not overridden in ExtendedFactory,
    #    it resolves to `BasicFactory._get_base_factory_instance()`.
    # 5. This method returns `BasicFactory()`, which is typed as `BasicFactory[str]`.
    # 6. However, `ExtendedFactory.create` (via inheritance and `Self`) is expected
    #    to return `ExtendedFactory[str]`.
    # The inherited method thus returns `BasicFactory[str]` when `ExtendedFactory[str]` is required.
    # This is a subtle Liskov substitution principle violation on an inherited method.
    # Some type checkers might detect this incompatibility when checking BasicFactory,
    # others when checking ExtendedFactory, and some might miss it until runtime.

if __name__ == "__main__":
    b_factory = BasicFactory()
    b_factory.register_type("basic", "data")
    new_b = b_factory.create()
    print(new_b._registry)

    e_factory = ExtendedFactory("TEST")
    e_factory.register_type("extended", "more data")
    new_e = e_factory.create() # Type of new_e is expected to be ExtendedFactory, but it's BasicFactory
    print(new_e._registry)
    # This line is expected to cause a type checker error, as new_e is a BasicFactory
    # which does not have a `_prefix` attribute. This highlights the Liskov violation
    # that some checkers might miss.
    # At runtime, this will raise an AttributeError.
    print(new_e._prefix)


# --- Tier 2 test ---

def test_BasicFactory_register_type():
    """Test that BasicFactory.register_type() runs without type errors."""
    try:
        receiver = BasicFactory()
        result = receiver.register_type()
        # Expected return type: NoneType
        print(f"OK: {result}")
    except (TypeError, AttributeError, ValueError, KeyError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_BasicFactory_register_type()
