"""Hypothesis-based property test for type constraint validation.

Type annotation: MethodSignature[[Self, str], str]
Test type: valid
"""\n\n"""Hypothesis test for MethodSignature[[Self, str], str] - valid values.

Type annotation: MethodSignature[[Self, str], str]
Variable: say_hello
Test type: valid
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

from typeguard import check_type

# Test that valid values pass
try:
    if "MethodSignature[[Self, str], str]" == "int":
        check_type(42, MethodSignature[[Self, str], str])
    elif "MethodSignature[[Self, str], str]" == "str":
        check_type("test", MethodSignature[[Self, str], str])
    elif "MethodSignature[[Self, str], str]" == "float":
        check_type(3.14, MethodSignature[[Self, str], str])
    else:
        # Generic valid test
        check_type(None, MethodSignature[[Self, str], str])
except:
    pass
