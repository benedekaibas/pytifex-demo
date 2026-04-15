"""
Hypothesis Tier 2 — Generated Test

Call: Dog()
Kind: constructor
Line: 60
Status: PASS
"""

# --- Original source (full context) ---

from typing import TypeGuard, List, Union, TypeVar, reveal_type, Protocol

T = TypeVar('T')
S = TypeVar('S')

# A generic TypeGuard function to check if all elements in a list are of a specific type.
def all_instances_of[T, S](items: List[T], cls: type[S]) -> TypeGuard[List[S]]:
    """TypeGuard to check if all items in a list are instances of cls.
    This function will cause a TypeError at runtime if `cls` is a Protocol,
    as `isinstance()` does not support protocols. Some type checkers (like mypy)
    will catch this statically, leading to divergence.
    """
    return all(isinstance(item, cls) for item in items) # <-- This line is the source of divergence

class Animal: pass
class Dog(Animal): pass
class Cat(Animal): pass

# --- NEW: Introduce a Protocol ---
class Barkable(Protocol):
    def bark(self) -> str: ...

class RealDog(Dog):
    def bark(self) -> str:
        return "Woof! (real)"

class FakeDog(Animal): # Not a Dog, but implements Barkable
    def bark(self) -> str:
        return "Woof! (fake)"

# The process_animals function now accepts lists that might contain Barkable objects
def process_animals(animals: List[Union[Animal, str, Barkable]]):
    if all_instances_of(animals, Dog):
        for dog in animals:
            reveal_type(dog) # Expected: Dog. (Most checkers will agree here)
            print(f"Woof! This is a dog: {dog}")
    elif all_instances_of(animals, Cat):
        for cat in animals:
            reveal_type(cat) # Expected: Cat.
            print(f"Meow! This is a cat: {cat}")
    # --- NEW: This is the divergence point ---
    elif all_instances_of(animals, Barkable): # 'cls' here is the `Barkable` Protocol
        # Mypy and other strict checkers are expected to raise a static error here
        # because `isinstance()` does not support Protocols.
        # Other checkers might not, leading to a static divergence or runtime TypeError.
        for barker in animals:
            reveal_type(barker) # Expected: Barkable (if no static error)
            print(f"I am a barker: {barker.bark()}")
    else:
        for item in animals:
            reveal_type(item) # Expected: Union[Animal, str, Barkable] (minus types already handled).
            print(f"Just an animal, string, or unknown item: {item}")

if __name__ == "__main__":
    print("--- List 1 (Contains non-Dog animal) ---")
    list1: List[Union[Animal, str, Barkable]] = [Dog(), Dog(), Animal()]
    process_animals(list1)

    print("\n--- List 2 (All dogs) ---")
    list2: List[Union[Animal, str, Barkable]] = [Dog(), Dog()]
    process_animals(list2)

    print("\n--- List 3 (All cats) ---")
    list3: List[Union[Animal, str, Barkable]] = [Cat(), Cat()]
    process_animals(list3)

    print("\n--- List 4 (Mixed string and animal) ---")
    list4: List[Union[Animal, str, Barkable]] = ["hello", Dog()]
    process_animals(list4)

    print("\n--- List 5 (Mixed Barkable types - RealDog and FakeDog) ---")
    list5: List[Union[Animal, str, Barkable]] = [RealDog(), FakeDog()]
    # This call will trigger the 'elif all_instances_of(animals, Barkable):' branch.
    # A strict type checker like mypy will report an error on line 18 ('isinstance(item, cls)')
    # when 'cls' is `Barkable`. Other checkers might ignore this, or handle it differently.
    process_animals(list5)

    print("\n--- List 6 (Only FakeDog, which is Barkable but not Dog/Cat) ---")
    list6: List[Union[Animal, str, Barkable]] = [FakeDog(), FakeDog()]
    process_animals(list6)


# --- Tier 2 test ---

def test_Dog_constructor():
    """Test that Dog() can be constructed."""
    try:
        instance = Dog()
        print(f"OK: {instance}")
    except (TypeError, AttributeError, ValueError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_Dog_constructor()
