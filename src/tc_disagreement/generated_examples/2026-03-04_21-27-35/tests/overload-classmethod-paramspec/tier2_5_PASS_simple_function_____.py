"""
Hypothesis Tier 2 — Generated Property Test

Target: simple_function(...)
Kind: function
Line: 42
Status: PASS
Max examples: 30

Strategies:
  a: int -> integers(min_value=-1000, max_value=1000)
  b: str -> text(max_size=30)
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(a=..., b=...)
def test_simple_function(a, b):
    """Property test: simple_function() with generated inputs."""
    result = simple_function(a, b)


if __name__ == "__main__":
    test_simple_function()
