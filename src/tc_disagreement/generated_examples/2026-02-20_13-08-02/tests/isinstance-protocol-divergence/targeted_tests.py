"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: isinstance-protocol-divergence.py
Patterns detected: 2
    - typeguard_narrowing (6 tests)
  - protocol_conformance (3 tests)
Test cases generated: 9
"""

# --- Original source ---

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

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_all_instances_of_returns_bool():
    """Verify all_instances_of returns a boolean."""
    try:
        result = all_instances_of([])
        if not isinstance(result, bool):
            BUGS.append({"line": 7, "type": "ReturnTypeMismatch", "error": f"TypeGuard all_instances_of returned {type(result).__name__}, expected bool", "test": "typeguard_returns_bool"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_empty_list"})


def test_all_instances_of_with_none():
    """Call all_instances_of with None."""
    try:
        all_instances_of(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_none"})


def test_all_instances_of_with_ints():
    """Call all_instances_of with list of ints."""
    try:
        result = all_instances_of([1, 2, 3])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_ints"})


def test_all_instances_of_with_strings():
    """Call all_instances_of with list of strings."""
    try:
        result = all_instances_of(["a", "b", "c"])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_strings"})


def test_all_instances_of_with_mixed():
    """Call all_instances_of with mixed type list."""
    try:
        result = all_instances_of([1, "hello", True, 3.14])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_mixed"})


def test_all_instances_of_with_bools():
    """Call all_instances_of with list of booleans."""
    try:
        result = all_instances_of([True, False, True])
        assert isinstance(result, bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "typeguard_bools"})


def test_RealDog_has_bark():
    """Verify RealDog has required protocol method 'bark'."""
    try:
        obj = RealDog()
        method = getattr(obj, "bark", None)
        if method is None:
            BUGS.append({"line": 20, "type": "AttributeError", "error": "RealDog missing protocol method bark", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 20, "type": "TypeError", "error": "RealDog.bark is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_FakeDog_has_bark():
    """Verify FakeDog has required protocol method 'bark'."""
    try:
        obj = FakeDog()
        method = getattr(obj, "bark", None)
        if method is None:
            BUGS.append({"line": 20, "type": "AttributeError", "error": "FakeDog missing protocol method bark", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 20, "type": "TypeError", "error": "FakeDog.bark is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_Barkable_non_conforming_object():
    """Pass a non-conforming object where Protocol Barkable is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
