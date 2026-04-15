"""Hypothesis Tier 2 test artifact.

Annotation: str
Variable: classify_id.__return__
Resolved type: <class 'str'>
Status: PASS
"""

# --- Original source code (full context) ---
from typing import Union, TypeAlias, TypeVar, Literal, Any, Dict, List

# Inspired by mypy#18524 ("Statement is unreachable" with match on type objects).
# This focuses on matching against types defined using TypeAlias, especially when they are generic or unions.

T = TypeVar("T")

class Success[T]:
    def __init__(self, value: T) -> None:
        self.value = value

class Failure:
    def __init__(self, error: str) -> None:
        self.error = error

# FIX: Changed `Result[T]: TypeAlias = ...` to `type Result[T] = ...`
# This fixes a syntax error for Python 3.12+ generic TypeAliases (PEP 695)
# and is necessary for type checkers to parse the file correctly.
type Result[T] = Union[Success[T], Failure]

# MODIFICATION FOR DIVERGENCE:
# Changed SimpleID to be a Union of Literal strings.
# This makes the `case _:` branch in `classify_id` truly unreachable.
# type SimpleID = Union[int, str, Literal["N/A"]] # Original
type SimpleID = Literal["Start", "Middle", "End"] # <--- MODIFIED

def handle_result(res: Result[Dict[str, Any]]) -> str:
    """
    Processes a generic Result TypeAlias.
    The interesting part is the type narrowing for Success[Dict[str, Any]].
    """
    match res:
        case Success() as s:
            # `s` should be narrowed to Success[Dict[str, Any]].
            if "status" in s.value and s.value["status"] == "ok":
                return f"Operation succeeded with status OK. Data: {s.value}"
            return f"Operation succeeded. Value: {s.value}"
        case Failure() as f:
            # `f` should be narrowed to Failure.
            return f"Operation failed: {f.error}"
        case _:
            # This branch is logically unreachable because `Result` is an exhaustive union
            # of `Success` and `Failure`, and the patterns cover these.
            # However, type checkers often do not flag this for class-based unions
            # by default (even mypy with --warn-unreachable might not).
            return f"Unexpected result type: {res}"

def classify_id(identifier: SimpleID) -> str:
    """
    Classifies an ID based on its literal value.
    This function is designed to show divergence in unreachable code analysis.
    """
    match identifier:
        case "Start":
            return "Initial phase"
        case "Middle":
            return "Mid-process"
        case "End":
            return "Final stage"
        case _:
            # <--- REAL DIVERGENCE: Reachability of this branch
            # For `SimpleID = Literal["Start", "Middle", "End"]`, all possible values
            # are covered by the preceding cases. This `_` branch is truly unreachable.
            #
            # Checker Results (with appropriate flags, e.g., mypy --warn-unreachable):
            # - mypy: Will flag this as unreachable code.
            # - pyrefly: Will NOT flag this.
            # - zuban: Will NOT flag this.
            # - ty: Will NOT flag this.
            return f"Unexpected ID literal: {identifier}"

if __name__ == "__main__":
    print(handle_result(Success({"status": "ok", "data": [1, 2]})))
    print(handle_result(Success({"data": "just some data"})))
    print(handle_result(Failure("Network error")))

    print("\n--- Classify ID ---")
    print(classify_id("Start"))
    print(classify_id("Middle"))
    print(classify_id("End"))
    # Removed calls that would now be type errors (e.g., classify_id(10)),
    # as SimpleID is a Literal union, not a general int/str union anymore.
    # The focus is on static reachability analysis of the `_` case.

# --- Hypothesis test ---
from hypothesis import given, settings, strategies as st
from typeguard import check_type, TypeCheckError

# To reproduce: run this file directly
# Annotation under test: str
# check_type(value, str)
