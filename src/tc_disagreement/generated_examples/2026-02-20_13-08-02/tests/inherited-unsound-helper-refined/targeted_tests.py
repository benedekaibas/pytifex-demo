"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: inherited-unsound-helper-refined.py
Patterns detected: 1
    - decorator_signature (4 tests)
Test cases generated: 4
"""

# --- Original source ---

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

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_AbstractFactory_create_decorated_callable():
    """Verify decorated method AbstractFactory.create is callable."""
    try:
        obj = AbstractFactory()
        method = getattr(obj, "create", None)
        if method is None:
            BUGS.append({"line": 8, "type": "AttributeError", "error": "AbstractFactory has no method create after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 8, "type": "TypeError", "error": "AbstractFactory.create is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_AbstractFactory_create_no_args():
    """Call decorated AbstractFactory.create with no extra args."""
    try:
        obj = AbstractFactory()
        result = obj.create()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_AbstractFactory_register_type_decorated_callable():
    """Verify decorated method AbstractFactory.register_type is callable."""
    try:
        obj = AbstractFactory()
        method = getattr(obj, "register_type", None)
        if method is None:
            BUGS.append({"line": 12, "type": "AttributeError", "error": "AbstractFactory has no method register_type after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 12, "type": "TypeError", "error": "AbstractFactory.register_type is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 12, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_AbstractFactory_register_type_no_args():
    """Call decorated AbstractFactory.register_type with no extra args."""
    try:
        obj = AbstractFactory()
        result = obj.register_type()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 12, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


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
