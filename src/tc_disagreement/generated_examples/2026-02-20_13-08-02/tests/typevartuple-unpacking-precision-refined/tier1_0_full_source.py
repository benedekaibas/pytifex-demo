from typing import TypeVar, Tuple, reveal_type, TypeVarTuple, Any, Union, Never, List

# T is unused in this example, but kept for minimal modification from original.
T = TypeVar('T')
# Use TypeVarTuple for variable-length type parameters, introduced in Python 3.11
Ts = TypeVarTuple('Ts') 

# Helper function to explicitly define the return type for the middle part.
# This function is generic over Ts_in, and its return type explicitly uses List[Union[*Ts_in]].
# This structure often forces type checkers to instantiate Ts_in more precisely.
def get_middle_items[**Ts_in](items: Tuple[Any, *Ts_in, Any]) -> List[Union[*Ts_in]]:
    # This unpacks a tuple with a TypeVarTuple-defined middle part.
    # The type inference for 'middle_items' here should be list[Union[*Ts_in]].
    _, *middle_items, _ = items
    return middle_items

def process_flexible_message[**Ts](msg: Tuple[str, *Ts, bool]):
    # This unpacks a tuple with a TypeVarTuple-defined middle part.
    # The type inference for 'middle' needs to correctly capture the variable part.
    start_tag, *middle, is_complete = msg

    # Reveal types to see how each checker infers them.
    # The original reveal_type(middle) might still yield list[object] for some checkers,
    # as observed in the initial test, indicating conservative inference for direct unpacking.
    reveal_type(start_tag)    # Expected: str
    reveal_type(middle)       # Original target, likely list[object] for many checkers
    reveal_type(is_complete)  # Expected: bool

    print(f"Start Tag: {start_tag}")
    print(f"Middle Parts: {middle}")
    print(f"Is Complete: {is_complete}")

    # NEW DIVERGENCE POINT: Call a helper function that returns an explicit List[Union[*Ts]].
    # This method of explicitly binding a TypeVarTuple to a generic function's return type
    # often leads to more precise inference in some type checkers (e.g., mypy, pyright)
    # compared to direct tuple unpacking within the function.
    precise_middle = get_middle_items(msg)
    reveal_type(precise_middle) # EXPECTED DIVERGENCE:
                                # - Precise checkers: list[Union[...]] (e.g., list[int | float | str])
                                # - Less precise/conservative checkers: list[Any] or list[object]
    print(f"Precise Middle (via helper): {precise_middle}")


if __name__ == "__main__":
    print("--- Test Case 1: Varied types in the middle ---")
    # For `precise_middle`, expected: list[int | float | str]
    process_flexible_message(("START", 1, 2.0, "hello", True))
    print("\n--- Test Case 2: Empty middle part ---")
    # For `precise_middle`, expected: list[Never]
    process_flexible_message(("EMPTY", False))
    print("\n--- Test Case 3: Single, specific type in the middle ---")
    # For `precise_middle`, expected: list[dict[str, str]]
    process_flexible_message(("SINGLE", {"key": "val"}, True))
    print("\n--- Test Case 4: Homogeneous types in the middle ---")
    # For `precise_middle`, expected: list[int]
    process_flexible_message(("HOMOGENEOUS", 10, 20, 30, True))

    # The divergence is now specifically targeted for 'precise_middle'.
    # While 'middle' (from direct unpacking) might still yield list[object] across all checkers,
    # 'precise_middle' (from the generic helper with an explicit List[Union[*Ts]] return)
    # is expected to show more precise inference (e.g., list[int | float | str]) in some checkers
    # that handle TypeVarTuple resolution more thoroughly, while others might remain conservative.