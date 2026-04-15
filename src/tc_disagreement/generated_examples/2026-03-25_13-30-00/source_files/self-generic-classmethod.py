from typing import TypeVar, Generic, Self

T = TypeVar("T")


class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    @classmethod
    def create(cls, value: T) -> Self:
        return cls(value)

    def get(self) -> T:
        return self.value


c: Container[int] = Container.create(42)
reveal_type(c)
reveal_type(c.get())

if __name__ == "__main__":
    pass
