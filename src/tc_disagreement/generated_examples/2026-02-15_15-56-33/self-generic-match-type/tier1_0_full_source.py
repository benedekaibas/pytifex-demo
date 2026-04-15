from typing import TypeVar, Self, Union, Any
import copy

# Inspired by mypy#18524 (match on type objects) and Self-type challenges.
# This tests how 'Self' in a generic class interacts with type checks in a match statement,
# specifically trying to match on the *type* of a Self-returned object.

T = TypeVar("T")

class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value

    def copy(self) -> Self:
        """Returns a copy of itself. The return type is Self."""
        # type(self) ensures the exact subclass type is instantiated.
        return type(self)(copy.deepcopy(self.value))

    def unwrap(self) -> T:
        """Returns the inner value."""
        return self.value

class IntBox(Box[int]):
    def double(self) -> Self:
        """Returns a new IntBox with doubled value."""
        return type(self)(self.value * 2)

class StrBox(Box[str]):
    def upper(self) -> Self:
        """Returns a new StrBox with uppercase value."""
        return type(self)(self.value.upper())

def inspect_box_return(box_instance: Union[Box[Any], IntBox, StrBox]) -> str:
    """
    Inspects a box instance, specifically its return type when `copy()` is called.
    We are trying to match on the *type object* of `box_instance.copy()`.
    """
    copied_box = box_instance.copy()
    
    # Python 3.10+ match can match against type objects.
    # The original mypy#18524 had `match field_type: case builtins.int:`.
    # Here, we use `type(IntBox(0))` to get the *type object* `IntBox`.
    match type(copied_box):
        case type(IntBox(0)): # Matches if `type(copied_box)` is `IntBox`
            # Here, `copied_box` should be narrowed to `IntBox`.
            # Checkers should allow `copied_box.unwrap() * 3`.
            return f"Copied an IntBox. Value: {copied_box.unwrap() * 3}"
        case type(StrBox("")): # Matches if `type(copied_box)` is `StrBox`
            # Here, `copied_box` should be narrowed to `StrBox`.
            # Checkers should allow `copied_box.unwrap().lower()`.
            return f"Copied a StrBox. Value: {copied_box.unwrap().lower()}"
        case type(Box(None)): # Matches if `type(copied_box)` is `Box`
            # Here, `copied_box` should be narrowed to `Box[Any]`.
            return f"Copied a generic Box. Value: {copied_box.unwrap()}"
        case _:
            # This case should ideally not be reachable if all `Box` subclasses of `box_instance`
            # were explicitly listed or if the checker is smart enough to know all possibilities.
            # Given that `Box` is generic and new subclasses could exist, this might be reachable.
            # The divergence is whether the checker marks this as "unreachable" (false positive) or not.
            return f"Copied an unknown Box type: {type(copied_box).__name__}" # <--- EXPECTED DIVERGENCE: Reachability

if __name__ == "__main__":
    ib = IntBox(5)
    sb = StrBox("Hello")
    gb = Box(True) # Generic Box

    print(inspect_box_return(ib))
    print(inspect_box_return(sb))
    print(inspect_box_return(gb))

    # Add a new Box type (not explicitly covered in match cases)
    class FloatBox(Box[float]):
        pass
    fb = FloatBox(3.14)
    print(inspect_box_return(fb)) # Should go to "unknown Box type"