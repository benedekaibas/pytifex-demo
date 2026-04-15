from typing import NewType, TypeVar

UserId = NewType("UserId", int)
AdminId = NewType("AdminId", int)

T = TypeVar("T", int, str)


def process_id(uid: UserId) -> None:
    reveal_type(uid)


def generic_func(val: T) -> T:
    return val


user: UserId = UserId(123)
process_id(user)

result: str = generic_func("hello")
reveal_type(result)

if __name__ == "__main__":
    pass
