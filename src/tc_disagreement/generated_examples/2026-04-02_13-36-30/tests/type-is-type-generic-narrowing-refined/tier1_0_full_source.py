from typing import TypeVar, Generic, NewType, reveal_type

UserId = NewType("UserId", int)
DeviceId = NewType("DeviceId", str)

T = TypeVar("T")

class BaseThing(Generic[T]):
    value: T

    def __init__(self, value: T) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        # mypy#20275 involves type(other) is reveal_type(type(self))
        # Here, we test if a generic instance with a NewType type argument
        # can be correctly compared based on type.
        if not (type(other) is type(self)):
            # Some checkers might struggle to see that type(self) includes the generic argument info
            # or that type(other) would match if `other` is also BaseThing[UserId]
            return NotImplemented
        # With reveal_type, mypy might correctly infer type(self) is Type[BaseThing[UserId]]
        # Without it, if `other` is BaseThing[DeviceId], `other.value` is str, not int.
        # This comparison should fail if types are different, but pass if they're the same class and generic param.
        reveal_type(type(self)) # Expect: `Type[BaseThing[UserId]]` when `self` is `BaseThing[UserId]`
        
        # The `type: ignore[attr-defined]` has been removed.
        # This forces type checkers to determine if `other` is correctly narrowed from `object`
        # to a type compatible with `BaseThing[T]` (or `Self`) by the `type(other) is type(self)` check.
        # Some checkers, especially those that correctly infer `type(self)` as `Type[Self]`,
        # might allow `other.value` to be accessed, while others that lose generic information
        # or don't narrow sufficiently will flag an error (e.g., `object` has no `value` attribute).
        return self.value == other.value


if __name__ == "__main__":
    user_thing = BaseThing(UserId(123))
    another_user_thing = BaseThing(UserId(456))
    device_thing = BaseThing(DeviceId("abc"))

    print(f"user_thing == another_user_thing: {user_thing == another_user_thing}")
    print(f"user_thing == device_thing: {user_thing == device_thing}")
    assert user_thing == another_user_thing # Should be True
    assert not (user_thing == device_thing) # Should be True