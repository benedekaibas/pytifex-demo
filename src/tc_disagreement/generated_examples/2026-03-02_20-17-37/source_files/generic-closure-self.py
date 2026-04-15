import typing as t
from typing import Generic, TypeVar, Callable, Self

T = TypeVar("T")

class Accumulator(Generic[T]):
    def __init__(self, initial_value: T, name: str = "default"):
        self._current_value = initial_value
        self.name = name

    def get_adder(self: Self) -> Callable[[T], None]:
        # The closure captures 'self' (and thus 'T' and 'name').
        # Type checkers might misinterpret 'Self' in this context,
        # especially when inferring the type of 'self._current_value' within the closure.
        def adder(new_value: T) -> None:
            reveal_type(self._current_value) # Expected: T
            print(f"[{self.name}] Adding {new_value} to {self._current_value}")
            # This line requires T to support '+'
            self._current_value = t.cast(T, self._current_value + new_value) # type: ignore
        return adder

    def get_current_value(self: Self) -> T:
        return self._current_value

if __name__ == "__main__":
    int_acc = Accumulator[int](0, "IntegerAccumulator")
    int_adder = int_acc.get_adder()
    reveal_type(int_adder) # Expected: Callable[[int], None]

    int_adder(5)
    int_adder(10)
    print(f"Current int value: {int_acc.get_current_value()}")

    str_acc = Accumulator[str]("", "StringConcatenator")
    str_adder = str_acc.get_adder()
    reveal_type(str_adder) # Expected: Callable[[str], None]

    str_adder("Hello, ")
    str_adder("World!")
    print(f"Current str value: {str_acc.get_current_value()}")