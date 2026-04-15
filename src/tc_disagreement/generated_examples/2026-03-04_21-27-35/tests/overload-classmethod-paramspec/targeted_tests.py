"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: overload-classmethod-paramspec.py
Patterns detected: 2
    - decorator_signature (4 tests)
  - main_block_replay (2 tests)
Test cases generated: 6
"""

# --- Original source ---

from typing import overload, Any, Callable, TypeVar, ParamSpec
from typing_extensions import reveal_type

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")

class Factory:
    _registry: dict[str, Callable[..., Any]] = {}

    @classmethod
    @overload
    def register(cls, name: str) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
    @classmethod
    @overload
    def register(cls, func: Callable[P, R], name: str | None = None) -> Callable[P, R]: ...
    @classmethod
    def register(cls, *args: Any, **kwargs: Any) -> Any:
        # Implementation detail not relevant for type checking disagreement.
        if len(args) == 1 and isinstance(args[0], str): # Decorator with name
            name = args[0]
            def decorator(func: Callable[P, R]) -> Callable[P, R]:
                cls._registry[name] = func
                return func
            return decorator
        elif len(args) >= 1 and callable(args[0]): # Direct call with func
            func = args[0]
            name = kwargs.get('name')
            if name is None:
                name = func.__name__
            cls._registry[name] = func
            return func
        else:
            raise TypeError("Invalid usage of register")

    @classmethod
    def create(cls, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in cls._registry:
            raise ValueError(f"No factory registered for {name}")
        return cls._registry[name](*args, **kwargs)

def simple_function(a: int, b: str) -> str:
    return f"Simple: {a}, {b}"

class MyClass:
    def __init__(self, x: int) -> None:
        self.x = x
    def greet(self) -> str:
        return f"Hello from MyClass with x={self.x}"

if __name__ == "__main__":
    @Factory.register("my_simple_func")
    def decorated_func(arg1: int, arg2: float) -> float:
        return arg1 + arg2

    reveal_type(decorated_func) # Expected: Callable[[int, float], float]

    result1 = Factory.create("my_simple_func", 10, 20.5)
    reveal_type(result1) # Expected: float

    Factory.register(simple_function, name="simple_math")
    result2 = Factory.create("simple_math", 5, "test")
    reveal_type(result2) # Expected: str

    Factory.register(MyClass) # Registers MyClass constructor
    obj = Factory.create("MyClass", 100)
    reveal_type(obj) # Expected: MyClass
    print(obj.greet())

    # This should be a type error on parameters if checker correctly infers P for 'decorated_func'
    # but some checkers might be too lax with ParamSpec in overloaded contexts.
    # Factory.create("my_simple_func", "wrong", "args")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_Factory_register_decorated_callable():
    """Verify decorated method Factory.register is callable."""
    try:
        obj = Factory()
        method = getattr(obj, "register", None)
        if method is None:
            BUGS.append({"line": 13, "type": "AttributeError", "error": "Factory has no method register after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 13, "type": "TypeError", "error": "Factory.register is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 13, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Factory_register_decorated_callable():
    """Verify decorated method Factory.register is callable."""
    try:
        obj = Factory()
        method = getattr(obj, "register", None)
        if method is None:
            BUGS.append({"line": 16, "type": "AttributeError", "error": "Factory has no method register after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 16, "type": "TypeError", "error": "Factory.register is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 16, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Factory_register_decorated_callable():
    """Verify decorated method Factory.register is callable."""
    try:
        obj = Factory()
        method = getattr(obj, "register", None)
        if method is None:
            BUGS.append({"line": 18, "type": "AttributeError", "error": "Factory has no method register after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 18, "type": "TypeError", "error": "Factory.register is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Factory_register_no_args():
    """Call decorated Factory.register with no extra args."""
    try:
        obj = Factory()
        result = obj.register()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_main_call_Factory_register_simple_function__name__():
    """Execute main block call: Factory.register(simple_function, name='simple_math')"""
    import traceback as _tb, sys as _sys
    try:
        Factory.register(simple_function, name='simple_math')
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 61
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_Factory_register_MyClass_():
    """Execute main block call: Factory.register(MyClass)"""
    import traceback as _tb, sys as _sys
    try:
        Factory.register(MyClass)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 65
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


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
