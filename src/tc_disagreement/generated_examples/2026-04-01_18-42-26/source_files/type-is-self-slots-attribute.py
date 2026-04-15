from typing import Self

class SlottedPoint:
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self: Self, other: object) -> bool:
        # Mypy's original issue: `type(other) is type(self)` does not narrow `other`
        # enough to safely access attributes like `other.y`.
        # Here, `x` and `y` are defined by __slots__.
        # This tests if __slots__ (which guarantees attributes) changes checker behavior.
        if isinstance(other, SlottedPoint) and type(other) is type(self):
            # Accessing 'x' and 'y' after `type(other) is type(self)`
            # Some checkers might still flag `other.x` or `other.y` as potentially
            # not existing, despite the `__slots__` and `type` check.
            return other.x == self.x and other.y == self.y
        return NotImplemented

if __name__ == "__main__":
    p1 = SlottedPoint(1, 2)
    p2 = SlottedPoint(1, 2)
    p3 = SlottedPoint(3, 4)

    print(f"p1 == p2: {p1 == p2}")
    print(f"p1 == p3: {p1 == p3}")

    # Test with a different object that might have 'x' and 'y' but isn't a SlottedPoint
    class OtherPoint:
        x: int = 1
        y: int = 2
    op = OtherPoint()
    print(f"p1 == op: {p1 == op}") # Should be False, not an error