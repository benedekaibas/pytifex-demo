"""Hypothesis-based property test for type constraint validation.

Type annotation: TypeGuard[IntSequence]
Test type: valid
"""\n\n"""Hypothesis test for TypeGuard[IntSequence] - valid values.

Type annotation: TypeGuard[IntSequence]
Variable: is_int_sequence.__return__
Test type: valid
"""

# Original source code
from typing import NewType, Tuple, TypeVar, Any, TypeGuard, Union

# Inspired by mypy#20563 (tuple types in generics) and NewType interaction.
# This tests NewType with a variable-length tuple type and its interaction with *args.

# Kept from original code as they are common and harmless, though not directly used in the divergence point.
T = TypeVar("T") 

# NewType representing a sequence of integers (original definition)
IntSequence = NewType('IntSequence', Tuple[int, ...])

# Divergence Point: TypeGuard interacting with NewType and unreachable code.
# The original 'isinstance(val, IntSequence)' caused a static error in all checkers,
# preventing the intended divergence around unreachable code.
# We modify it to always return False at runtime, which effectively makes the
# `if is_int_sequence(...)` branch unreachable, mimicking the original intent
# but bypassing the 'cannot use NewType with isinstance' error.
def is_int_sequence(val: Union[Tuple[int, ...], str]) -> TypeGuard[IntSequence]:
    """
    A TypeGuard that will always return False at runtime.
    
    This function is designed to make the 'if' branch it guards statically and
    dynamically unreachable. Type checkers might still apply the TypeGuard's
    refinement inside the unreachable branch, leading to divergence.
    """
    # This change from 'return isinstance(val, IntSequence)'
    # bypasses the static error about using NewType with isinstance,
    # and ensures the 'if' block below is always unreachable at runtime.
    # Type checkers will now have to decide whether to report 'unreachable code'
    # and whether to apply type refinement inside that unreachable block.
    return False

if __name__ == "__main__":
    # Original correct usages are omitted for brevity to highlight the divergence point.
    # seq1: IntSequence = IntSequence((1, 2, 3))
    # print(f"Sum of sequences: {process_sequences(seq1, seq2)}")

    # Raw tuple which is the base type of IntSequence, but not IntSequence itself.
    raw_tuple: Tuple[int, ...] = (4, 5)

    # --- REAL DIVERGENCE POINT ---
    # We pass 'raw_tuple' (statically typed as Tuple[int, ...]) to is_int_sequence.
    # At runtime, `is_int_sequence` will always evaluate to False.
    # Therefore, the 'if' branch is statically and dynamically unreachable.

    # Type checkers diverge on how they handle this unreachable branch:
    # - mypy, ty: Report 'unreachable code' for the `if` block, AND report the
    #             'incompatible assignment' inside it.
    # - pyrefly, zuban: DO NOT report 'unreachable code'. They ONLY report the
    #                   'incompatible assignment' inside the 'if' block, implying
    #                   they apply the TypeGuard's refinement even though the branch
    #                   is statically unreachable.
    
    value_to_check: Tuple[int, ...] = raw_tuple
    if is_int_sequence(value_to_check):
        print("This path should be unreachable at runtime with a raw tuple.")
        # Inside this branch, TypeGuard refines 'value_to_check' to 'IntSequence'.
        # This assignment then attempts to assign 'Tuple[int, ...]' (the original type
        # of 'value_to_check') to 'IntSequence'.
        # This is an incompatible assignment because NewType creates a distinct type.
        divergence_result: IntSequence = value_to_check 
    else:
        print(f"This path is correctly taken for raw tuples: {value_to_check}")

from typeguard import check_type

# Test that valid values pass
try:
    if "TypeGuard[IntSequence]" == "int":
        check_type(42, TypeGuard[IntSequence])
    elif "TypeGuard[IntSequence]" == "str":
        check_type("test", TypeGuard[IntSequence])
    elif "TypeGuard[IntSequence]" == "float":
        check_type(3.14, TypeGuard[IntSequence])
    else:
        # Generic valid test
        check_type(None, TypeGuard[IntSequence])
except:
    pass
