from typing import TypeVar, Any, reveal_type, TypeGuard, Type

T = TypeVar("T")

class Box[T]:
    content: T
    def __init__(self, content: T) -> None:
        self.content = content

class SpecialBox(Box[str]):
    special_property: bool = True

def is_same_box_type[T](obj: Any, other_box: Box[T]) -> TypeGuard[Box[T]]:
    # This TypeGuard is fundamentally unsound with generics, as `type()` ignores type arguments.
    # E.g., `type(Box[int]()) is type(Box[str]())` is True.
    # All checkers currently trust this TypeGuard completely, even though it can be unsound.
    return type(obj) is type(other_box)

def process_content_with_type[T](b: Box[T], expected_content_type: Type[T]) -> T | None:
    # Statically, `b.content` is of type `T` and `expected_content_type` is `Type[T]`.
    # Therefore, type checkers should infer that `isinstance(b.content, expected_content_type)`
    # is always True, making the `if` branch (and `return None`) unreachable.
    #
    # However, if `b` was narrowed by an *unsound* TypeGuard (as `is_same_box_type` is),
    # `b.content` at runtime might not match `expected_content_type`.
    #
    # This creates a divergence point:
    # - Some checkers might strictly follow the static typing and consider the `if` branch
    #   unreachable, inferring the return type as `T`.
    # - Others might be more conservative, recognizing the potential for runtime mismatch
    #   given the preceding unsound TypeGuard, and infer the return type as `T | None`.
    if not isinstance(b.content, expected_content_type):
        print(f"RUNTIME MISMATCH: Expected content of type {expected_content_type.__name__}, got {type(b.content).__name__}.")
        return None
    return b.content

def process_boxes(box1: Box[int], box_or_any: Any) -> None:
    print(f"\nProcessing with box1={box1.content}, box_or_any={box_or_any}")
    if is_same_box_type(box_or_any, box1):
        # The TypeGuard `is_same_box_type` claims `box_or_any` is `Box[int]`.
        reveal_type(box_or_any) # Expect: Box[int] (all checkers agree here)

        # Call the new helper function.
        # `box_or_any` is statically `Box[int]`, so `T` is inferred as `int`.
        # `expected_content_type` is passed as `int` (which is `Type[int]`).
        #
        # For CASE 2 (`str_box`), `box_or_any.content` is "hello" at runtime,
        # but typed as `int` due to the unsound TypeGuard.
        # The `isinstance("hello", int)` check will be `False` at runtime.
        actual_content = process_content_with_type(box_or_any, int)
        reveal_type(actual_content) # Divergence point: Expect `int` vs `int | None`

        if actual_content is not None:
            # This line will cause a runtime TypeError for `CASE 2` if the helper returns
            # the original string (which would then be typed as `int` by trust in TypeGuard).
            # If `actual_content` is typed as `int | None`, some checkers might flag `actual_content + 1`
            # as an error unless `None` is explicitly handled.
            print(f"Processed content result: {actual_content + 1}")
        else:
            print("Content type mismatch prevented further processing.")
    else:
        print("Different box type or not a box.")

if __name__ == "__main__":
    int_box = Box(10)
    str_box = Box("hello") # Box[str]
    special_str_box = SpecialBox("world") # SpecialBox[str]

    # CASE 1: Matches exactly (Box[int] -> Box[int])
    # All checkers should pass this and reveal Box[int], and int.
    process_boxes(int_box, Box(20))

    # CASE 2: Base classes match, but generic arguments differ (Box[str] -> Box[int])
    # The TypeGuard `type(Box[str]) is type(Box[int])` evaluates to True.
    # So `box_or_any` (originally Box[str]) is narrowed to `Box[int]`.
    # The `process_content_with_type` helper will then perform `isinstance("hello", int)`,
    # which is False at runtime. This will return `None`.
    # Checkers are expected to diverge on the revealed type of `actual_content` (int vs int | None)
    # and whether to flag `actual_content + 1` as an error if `None` is considered reachable.
    process_boxes(int_box, str_box)

    # CASE 3: Subclass, so types do not match (SpecialBox -> Box[int])
    # All checkers should not narrow, as `type(SpecialBox)` is not `type(Box)`.
    process_boxes(int_box, special_str_box)

    # CASE 4: Not a box
    # All checkers should not narrow.
    process_boxes(int_box, "not a box")