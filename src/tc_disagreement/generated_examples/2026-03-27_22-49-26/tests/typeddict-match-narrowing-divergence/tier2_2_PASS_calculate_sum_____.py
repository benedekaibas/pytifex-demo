"""
Hypothesis Tier 2 — Generated Property Test

Target: calculate_sum(...)
Kind: function
Line: 23
Status: PASS
Max examples: 30

Strategies:
  a: int -> integers(min_value=-1000, max_value=1000)
  b: int -> integers(min_value=-1000, max_value=1000)
"""

# --- Original source (full context) ---

from typing import Callable, ParamSpec, TypeVar, Union, TYPE_CHECKING, Literal, TypedDict, Any
import functools

P = ParamSpec('P')
R = TypeVar('R')

def custom_logger(prefix: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Added type: ignore for func.__name__ to satisfy stricter checkers like ty
            # which might flag Callable[P, R] not guaranteeing __name__
            print(f"[{prefix}] Calling '{func.__name__}'") # type: ignore[attr-defined]
            return func(*args, **kwargs)
        return wrapper
    return decorator

@custom_logger("APP")
def greet_user(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

@custom_logger("MATH")
def calculate_sum(a: int, b: int) -> int:
    return a + b

@custom_logger("UNKNOWN")
def no_args_func() -> Literal["done"]:
    return "done"

# Changed from Dict[str, Union[...]] to TypedDict for more precise type information
# for each key. This should help type checkers narrow the type of 'target_func'
# when using structural pattern matching, leading to divergence if some checkers
# narrow correctly and others do not.
class FunctionRegistry(TypedDict):
    greet_user: Union[
        Callable[[str, str], str], # For greet_user requiring both args
        Callable[[str], str]       # For greet_user using default greeting
    ]
    calculate_sum: Callable[[int, int], int]
    no_args_func: Callable[[], Literal["done"]]


def process_registry_entry(key: str, entry: FunctionRegistry):
    # The `match entry:` syntax attempts to structurally match the dictionary.
    # When a key like "greet_user" is matched, `target_func` should ideally
    # take on the type associated with that key in the `TypedDict` definition.
    # This is where divergence is expected: some checkers might correctly narrow
    # `target_func` based on the TypedDict, while others might fail to do so,
    # leading to different results for the intentional type error below.
    match entry:
        case {"greet_user": target_func}:
            if TYPE_CHECKING:
                # Explicit import for reveal_type within TYPE_CHECKING to prevent
                # runtime issues with checkers that might try to import it.
                from typing import reveal_type
                # Expected: Union[Callable[[str, str], str], Callable[[str], str]]
                # Divergence point: Some checkers might still reveal the full union
                # of all callables defined in the original `Dict`-like type.
                reveal_type(target_func)
            print(f"Matched greet_user (2 args): {target_func('Alice', 'Hi')}")
            print(f"Matched greet_user (1 arg): {target_func('Bob')}")
            # --- INTENTIONAL TYPE ERROR FOR DIVERGENCE ---
            # Calling `target_func` (which should be `greet_user`'s type) with integer arguments.
            # This should be a type error if `target_func` has been correctly narrowed
            # to `Union[Callable[[str, str], str], Callable[[str], str]]`
            # (the TypedDict value for 'greet_user').
            #
            # If `target_func` is *not* correctly narrowed (e.g., still includes
            # `Callable[[int, int], int]` from `calculate_sum`), then some checkers
            # might *not* flag `target_func(1, 2)` as an error, as it would match
            # the signature of `calculate_sum`. This difference in error detection
            # constitutes the divergence.
            print(f"Attempting to call greet_user with int args (EXPECTED ERROR FOR SOME CHECKERS): {target_func(1, 2)}")
        case {"calculate_sum": target_func}:
            if TYPE_CHECKING:
                from typing import reveal_type
                # Expected: Callable[[int, int], int]
                reveal_type(target_func)
            print(f"Matched calculate_sum: {target_func(5, 7)}")
        case {"no_args_func": target_func}:
            if TYPE_CHECKING:
                from typing import reveal_type
                # Expected: Callable[[], Literal["done"]]
                reveal_type(target_func)
            print(f"Matched no_args_func: {target_func()}")
        case _:
            # This case won't be hit with the current `if __name__ == "__main__"` calls,
            # as `entry` is always the full `registry` TypedDict which contains all keys.
            print(f"No specific pattern match for the structure of {key}.")

if __name__ == "__main__":
    registry: FunctionRegistry = {
        "greet_user": greet_user,
        "calculate_sum": calculate_sum,
        "no_args_func": no_args_func
    }

    print("--- Processing registry entries ---")
    # Call `process_registry_entry` with the full `registry` and a dummy key,
    # consistent with the original example's structure.
    # The `match` statement inside `process_registry_entry` will
    # then match `entry` (which is the `registry` object itself).
    process_registry_entry("greet_user", registry)
    process_registry_entry("calculate_sum", registry)
    process_registry_entry("no_args_func", registry)
    process_registry_entry("unknown_key", registry) # This will hit the `case _` as no key matches `key`
                                                  # in the match pattern `{"key": var}` on `entry`.


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(a=..., b=...)
def test_calculate_sum(a, b):
    """Property test: calculate_sum() with generated inputs."""
    result = calculate_sum(a, b)


if __name__ == "__main__":
    test_calculate_sum()
