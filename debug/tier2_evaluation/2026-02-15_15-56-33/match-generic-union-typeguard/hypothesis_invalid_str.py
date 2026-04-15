"""Hypothesis-based property test for type constraint validation.

Type annotation: str
Test type: invalid
"""\n\n"""Hypothesis test for str - invalid values.

Type annotation: str
Variable: process_union_data.__return__
Test type: invalid
"""

# Original source code
from typing import Union, Literal, TypeVar, TypeGuard, Any
from decimal import Decimal

# Inspired by mypy#18524's "unreachable" warning with match on type objects.
# Here, we match on values, but the value's type is a generic Union, and we use TypeGuard.

T = TypeVar("T")

class Foo[T]:
    value: T
    def __init__(self, value: T) -> None:
        self.value = value

class Bar[T]:
    value: T
    def __init__(self, value: T) -> None:
        self.value = value

# A TypeGuard that checks if a Foo instance holds a specific literal string.
def is_foo_literal_string_one(val: Foo[Any]) -> TypeGuard[Foo[Literal["one"]]]:
    # val is Foo[Union[T, Literal["one"]]]
    return isinstance(val, Foo) and val.value == "one"

def process_union_data[V](data: Union[Foo[V], Bar[V], Literal["raw", "other_raw"]]) -> str:
    """
    Processes a union type that can be a generic Foo, a generic Bar, or a raw literal string.
    The goal is to see how type checkers handle narrowing when a TypeGuard is used in a match case,
    especially with generics and literals.
    """
    match data:
        case Foo() as f if is_foo_literal_string_one(f): # Use TypeGuard here
            # Here, f should be narrowed to Foo[Literal["one"]] by strict checkers.
            return f"Foo with literal 'one': {f.value}"
        case Foo() as f:
            # Here, f should be narrowed to Foo[V] where V is not Literal["one"].
            return f"Generic Foo: {f.value}"
        case Bar() as b:
            # Here, b should be narrowed to Bar[V].
            return f"Generic Bar: {b.value}"
        case "raw" | "other_raw": # Multiple literal matches
            # This should correctly narrow to Literal["raw"] | Literal["other_raw"]
            return f"Raw string: {data}"
        case _:
            # mypy#18524 had "unreachable" here for a different `match` scenario.
            # With complex unions and guards, will a checker incorrectly determine exhaustiveness here?
            # E.g., if V could be `None`, `Foo[None]` wouldn't match previous cases.
            return f"Unhandled case: {data}" # <--- EXPECTED DIVERGENCE: Reachability of this branch

if __name__ == "__main__":
    print(process_union_data(Foo("one")))
    print(process_union_data(Foo(123)))
    print(process_union_data(Bar("test")))
    print(process_union_data("raw"))
    print(process_union_data("other_raw"))
    print(process_union_data(Foo(Decimal("1.23"))))
    
    # This should hit the '_' case, assuming V can be `None`.
    print(process_union_data(Foo(None)))

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, str)
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "str" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "str" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
