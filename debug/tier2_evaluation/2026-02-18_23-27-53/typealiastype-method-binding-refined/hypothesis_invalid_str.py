"""Hypothesis-based property test for type constraint validation.

Type annotation: str
Test type: invalid
"""\n\n"""Hypothesis test for str - invalid values.

Type annotation: str
Variable: name
Test type: invalid
"""

# Original source code
from typing import TypeAliasType, Callable, Self, ParamSpec, TypeVar, reveal_type

P = ParamSpec('P')
R = TypeVar('R')

# Define a TypeAliasType for a generic callable signature
MethodSignature = TypeAliasType('MethodSignature', Callable[P, R], type_params=(P, R))

# A function matching a potential MethodSignature
# The original issue was 'Self' being used outside a class in greet_func.
# By replacing 'Self' with the concrete class 'Greeter', we fix this primary error.
# The 'cast' is also no longer needed as 'self' is explicitly typed.
def greet_func(self: Greeter, name: str) -> str:
    return f"Hello from {self.__class__.__name__}, {name}!"

class Greeter:
    name: str = "Default"
    
    # Assign the function using the TypeAliasType
    # Here, 'Self' correctly resolves to 'Greeter'.
    # So say_hello is expected to be Callable[[Greeter, str], str] before binding.
    say_hello: MethodSignature[[Self, str], str] = greet_func

def test_typealiastype_method():
    g = Greeter()
    # The divergence is expected here:
    # Some type checkers might correctly infer 'Callable[[str], str]'
    # after 'self' is bound (like for a regular method).
    # Others might retain the unbound type 'Callable[[Greeter, str], str]',
    # or even 'Any' if they struggle with TypeAliasType and method binding.
    reveal_type(g.say_hello) # Expected: Callable[[str], str] (after binding self)
    reveal_type(g.say_hello("World")) # Expected: str
    
if __name__ == "__main__":
    test_typealiastype_method()

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
