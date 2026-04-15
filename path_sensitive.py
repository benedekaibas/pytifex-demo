"""Demonstrate how path sensitive analysis works through a simple code example."""
from typing import List

class Shape:
    def draw(self):
        print(Shape)

class Square(Shape):
    def get_side_length(self, side: int) -> str:
        return f"The length of the side of this square is: {side}"

class Circle(Shape):
    def get_radius(self, diameter: int):
        return diameter / 2

def add_shape_to_list(shape: list[Shape]):
    shape.append(Circle())

if __name__ == "__main__":
    spongebob: list[Square] = [Square()]
    add_shape_to_list(spongebob)
    print("There is no Type Error in this file!")
