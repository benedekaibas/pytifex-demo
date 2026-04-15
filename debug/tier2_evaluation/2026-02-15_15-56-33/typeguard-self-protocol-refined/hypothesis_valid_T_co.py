"""Hypothesis-based property test for type constraint validation.

Type annotation: T_co
Test type: valid
"""\n\n"""Hypothesis test for T_co - valid values.

Type annotation: T_co
Variable: value.__return__
Test type: valid
"""

# Original source code
from typing import Protocol, TypeGuard, Self, runtime_checkable, Union, TypeVar, assert_type

# Inspired by mypy#18524 (match on type objects), exploring TypeGuard with Self.
# This tests if type checkers correctly handle 'Self' in a TypeGuard when used in a protocol context,
# especially when multiple concrete types might implement it.

T_co = TypeVar('T_co', covariant=True) # MODIFIED: Changed T to T_co and made it covariant

@runtime_checkable
class Validatable(Protocol[T_co]): # MODIFIED: Used T_co
    @property # MODIFIED: Made 'value' a read-only property to allow covariance
    def value(self) -> T_co:
        """The value managed by the entity."""
        ...
    # MODIFIED: Reverted return type to TypeGuard[Self] as originally intended
    def is_valid(self) -> TypeGuard[Self]:
        """Returns True if the instance is considered valid."""
        ...

class User(Validatable[str]):
    _value: str # MODIFIED: Store value internally for the property
    _is_active: bool
    def __init__(self, name: str, is_active: bool) -> None:
        self._value = name
        self._is_active = is_active

    @property # MODIFIED: Implement the property
    def value(self) -> str:
        return self._value

    # MODIFIED: Reverted return type to TypeGuard[Self]
    def is_valid(self) -> TypeGuard[Self]:
        return self._is_active and len(self.value) > 0

class Product(Validatable[float]):
    _value: float # MODIFIED: Store value internally for the property
    _in_stock: int
    def __init__(self, price: float, in_stock: int) -> None:
        self._value = price
        self._in_stock = in_stock

    @property # MODIFIED: Implement the property
    def value(self) -> float:
        return self._value

    # MODIFIED: Reverted return type to TypeGuard[Self]
    def is_valid(self) -> TypeGuard[Self]:
        return self._in_stock > 0 and self.value > 0.0

# With T_co being covariant, Validatable[str] is now a subtype of Validatable[Union[str, float]].
# This fixes the initial 'arg-type' error observed by all checkers.
def process_entity(entity: Validatable[Union[str, float]]) -> str:
    """
    Processes a validatable entity. After is_valid(), the type should ideally be narrowed
    to the specific concrete type (User or Product), allowing access to its specific members.
    """
    if entity.is_valid():
        # After `entity.is_valid()`, TypeGuard[Self] narrows `entity` to its concrete runtime type.
        # This means `entity` is known to be a concrete implementation of `Validatable`,
        # but its specific type (e.g., `User`, `Product`, or another `Validatable` implementor)
        # is still unknown at this point. The `isinstance` checks perform further narrowing.
        if isinstance(entity, User):
            # After isinstance, entity is narrowed to User.
            return f"Valid User: {entity.value} (active: {entity._is_active})"
        elif isinstance(entity, Product):
            # After isinstance, entity is narrowed to Product.
            return f"Valid Product: {entity.value} (in stock: {entity._in_stock})"
        else:
            # EXPECTED DIVERGENCE: Reachability of this else-block.
            # - Some checkers may mark this as unreachable if they can prove (via whole-program
            #   analysis, for example) that `User` and `Product` are the *only* concrete
            #   implementations of `Validatable[str]` or `Validatable[float]` in the program.
            # - Mypy typically marks this as reachable because `Validatable[Union[str, float]]`
            #   could theoretically be any other concrete class implementing the protocol
            #   (e.g., `class AnotherValidatable(Validatable[str]): ...`), which would pass
            #   the type checks but fall into this `else` at runtime.
            return f"Valid but unknown entity type: {entity.value} (runtime type: {type(entity).__name__})"
    else:
        return f"Invalid entity: {entity.value}"

if __name__ == "__main__":
    user_active = User("Alice", True)
    user_inactive = User("", False)
    product_available = Product(19.99, 5)
    product_out_of_stock = Product(0.0, 0)

    print(process_entity(user_active))
    print(process_entity(user_inactive))
    print(process_entity(product_available))
    print(process_entity(product_out_of_stock))

from typeguard import check_type

# Test that valid values pass
try:
    if "T_co" == "int":
        check_type(42, T_co)
    elif "T_co" == "str":
        check_type("test", T_co)
    elif "T_co" == "float":
        check_type(3.14, T_co)
    else:
        # Generic valid test
        check_type(None, T_co)
except:
    pass
