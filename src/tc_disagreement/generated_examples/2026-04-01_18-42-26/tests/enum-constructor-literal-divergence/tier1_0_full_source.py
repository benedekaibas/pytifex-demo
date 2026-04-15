import enum
from typing import TypeGuard, reveal_type, Union, Self, Literal

class Status(enum.StrEnum): # Requires Python 3.11+
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

    # --- MODIFICATION START ---
    # Explicitly hint the constructor's input to be very restrictive.
    # This forces type checkers to consider if a plain 'str' (from user_status_str)
    # is compatible with 'Literal' or 'Self'.
    # This stricter signature might cause divergence among type checkers:
    # 1. Some might respect this specific override and flag the use of a plain `str`
    #    where a `Literal` or `Self` is expected.
    # 2. Others might ignore this override due to complex `enum` metaclass behavior
    #    or their internal understanding of `Enum` constructors, and still allow `str`.
    # 3. Some might even flag the definition of `__new__` itself as incompatible
    #    with the base `enum.Enum`'s more permissive `__new__` signature (`value: Any`).
    def __new__(cls, value: Union[Self, Literal["active", "inactive", "pending"]]) -> Self:
        # Delegating to super() ensures runtime correctness.
        # The type hint here is solely to provoke type checker divergence.
        return super().__new__(cls, value)
    # --- MODIFICATION END ---

def get_input_str() -> str:
    """
    Simulates getting a string from user input or a file.
    The type checker cannot statically know the exact value.
    """
    return "active"

def is_valid_status_str(s: str) -> TypeGuard[Status]:
    """TypeGuard to check if a string is a valid Status member."""
    return s in Status.__members__.values()

if __name__ == "__main__":
    user_status_str: str = get_input_str()
    unknown_status_str: str = "blocked"

    # Zuban's original issue about Enum constructor expecting a literal.
    # Here, we try to construct a StrEnum from a variable whose specific
    # string value is not known at type-checking time.
    # Some type checkers might flag this as potentially unsafe,
    # requiring explicit guarding or a Literal type, while others might
    # permit it as long as the type (`str`) is generally compatible.
    try:
        # This line is now expected to cause divergence:
        # 'user_status_str' has type 'str', but our custom __new__ expects
        # 'Union[Self, Literal["active", "inactive", "pending"]]'.
        # A plain 'str' is generally not assignable to a specific 'Literal' type.
        current_status = Status(user_status_str)
        print(f"Constructed status: {current_status}")
    except ValueError as e:
        print(f"Error constructing status: {e}")

    # Now, try with the TypeGuard.
    # All type checkers should agree that after the TypeGuard,
    # `user_status_str` is narrowed to `Status`.
    # This narrowing makes `user_status_str` compatible with the `Self`
    # part of the `__new__` signature, so this section should pass for all.
    if is_valid_status_str(user_status_str):
        reveal_type(user_status_str) # Should be narrowed to Status
        # If TypeGuard works, this should be fine for all checkers
        # because 'user_status_str' is now 'Status' (Self).
        guarded_status = Status(user_status_str)
        print(f"Guarded status: {guarded_status}")
    else:
        print(f"'{user_status_str}' is not a valid status (this path should not be taken for 'active').")


    if not is_valid_status_str(unknown_status_str):
        print(f"'{unknown_status_str}' is not a valid status.")