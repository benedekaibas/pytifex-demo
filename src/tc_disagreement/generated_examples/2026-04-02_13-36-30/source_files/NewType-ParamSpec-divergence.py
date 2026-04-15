from __future__ import annotations
from typing import TypeVar, Generic, NewType, reveal_type, Self, Callable, ParamSpec, Concatenate, Any, cast, SupportsInt
from dataclasses import dataclass
import functools

KeyId = NewType("KeyId", int)
# Changed: Key is now bound by SupportsInt to ensure `int(self.item)` is type-safe for all checkers.
# This prevents the initial error and focuses on the subsequent type mismatch.
Key = TypeVar("Key", bound=SupportsInt)

_P = ParamSpec("_P")
_T = TypeVar("_T") # TypeVar for the decorated function's return type

# This decorator is designed to create divergence.
# It explicitly casts the return value of the wrapped function to `Any` within the wrapper,
# but the wrapper's signature itself promises `_T`.
# Some type checkers might trust the `wrapper`'s signature (`-> _T`) more strongly
# due to `functools.wraps`, preserving the precise generic `Self` type.
# Others might follow the explicit `cast(Any, ...)` and effectively lose type information,
# treating the return as `Any`, or fail due to `Any` being assigned where a specific type is expected.
def potentially_divergent_decorator(f: Callable[_P, _T]) -> Callable[_P, _T]:
    @functools.wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        result = f(*args, **kwargs)
        # The key divergence point: casting to Any before returning.
        # For some checkers, this cast might "taint" the return type with Any,
        # leading to an error on assignment to `Self` later.
        # For others, `functools.wraps` (or their inference logic) might override
        # the explicit `cast(Any, ...)` and infer the original `Self` type correctly,
        # making them flag the *inner* assignment error more directly.
        return cast(Any, result) # This explicit cast to Any is the subtle trigger
    return wrapper

@dataclass(frozen=True)
class Box[Key]:
    item: Key
    size: int = 1

    # `grow` is now a regular method, and the logic that causes the type error
    # is encapsulated in a separate function that the decorator can modify.
    # The actual type error of `int` (from `item_val`) being passed where `KeyId` is expected
    # still occurs inside the `_grow_impl` call.
    def grow(self) -> Self:
        return self._grow_impl()

    # This is the function whose return value will be passed through the decorator.
    # It attempts to construct `Self` (e.g., `Box[KeyId]`) but passes an `int` for `item`.
    # Type checkers should flag this `int` to `KeyId` mismatch.
    # However, the decorator's `cast(Any, ...)` might interfere with how this error is reported,
    # or even allow it to pass for some checkers if `Any` is implicitly compatible with `Self`.
    @potentially_divergent_decorator
    def _grow_impl(self: Self) -> Self:
        item_val = int(cast(int, self.item)) # `item_val` is `int`
        # This is the original subtle type error: passing `int` where `KeyId` is expected.
        # The decorator's interaction is expected to cause a divergence here.
        return type(self)(item=item_val, size=self.size + 1) # <-- Divergence point

    def change_item(self, new_item: Key) -> Self:
        return type(self)(item=new_item, size=self.size)

if __name__ == "__main__":
    my_key = KeyId(42)
    my_box = Box(item=my_key) # 'Key' is inferred as 'KeyId' here
    reveal_type(my_box) # Expect: Box[KeyId]

    bigger_box = my_box.grow()
    reveal_type(bigger_box) # Expect: Box[KeyId] (if decorator's effect is consistent)

    new_key = KeyId(99)
    changed_box = bigger_box.change_item(new_key)
    reveal_type(changed_box)

    # Box(item=100) # This should still be a type error if KeyId is expected.
    # Example to show Box[object] is possible with Key = TypeVar("Key", KeyId, object)
    # my_box_obj = Box(item=100)
    # reveal_type(my_box_obj)