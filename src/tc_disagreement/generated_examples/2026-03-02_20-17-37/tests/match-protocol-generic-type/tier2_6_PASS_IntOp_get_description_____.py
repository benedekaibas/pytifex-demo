"""
Hypothesis Tier 2 — Generated Property Test

Target: IntOp.get_description(...)
Kind: method
Line: 14
Status: PASS
Max examples: 30
"""

# --- Original source (full context) ---

import typing as t
from typing import Protocol, TypeVar, Any, Callable, Generic

P_R = TypeVar("P_R")

class Operation(Protocol[P_R]):
    def perform(self) -> P_R: ...
    def get_description(self) -> str: ...
    def default_value(self) -> P_R: ... # Method with a generic return type default behavior

class IntOp:
    def perform(self) -> int:
        return 42
    def get_description(self) -> str:
        return "Integer operation"
    def default_value(self) -> int:
        return 0

class StrOp:
    def perform(self) -> str:
        return "hello"
    def get_description(self) -> str:
        return "String operation"
    def default_value(self) -> str:
        return ""

def process_operation_result[T](op: Operation[T]) -> T:
    value = op.perform()
    
    # Type checkers might struggle to infer T correctly here when matching against value.
    # The interaction of match with a generic TypeVar that's bound by a Protocol
    # can lead to inaccurate narrowing.
    match value:
        case int() as i: # If T is int, this should match
            reveal_type(i) # Expected: int
            print(f"Matched int: {i}")
            return i 
        case str() as s: # If T is str, this should match
            reveal_type(s) # Expected: str
            print(f"Matched str: '{s}'")
            return s
        case _:
            reveal_type(value) # Expected: T (original generic type)
            print(f"Matched unexpected type: {type(value).__name__} (Value: {value}). Using default.")
            return op.default_value()

if __name__ == "__main__":
    print(f"Result for IntOp: {process_operation_result(IntOp())}")
    print(f"Result for StrOp: {process_operation_result(StrOp())}")

    class FloatOp:
        def perform(self) -> float:
            return 3.14
        def get_description(self) -> str:
            return "Float operation"
        def default_value(self) -> float:
            return 0.0
    
    print(f"Result for FloatOp: {process_operation_result(FloatOp())}")


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(receiver=...)
def test_IntOp_get_description(receiver):
    """Property test: IntOp.get_description() with generated inputs."""
    result = receiver.get_description()
    # Expected return type: str


if __name__ == "__main__":
    test_IntOp_get_description()
