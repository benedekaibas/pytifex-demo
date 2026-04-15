"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 2
Skipped (no strategies): 1
Bugs found: 0

Plan 0: [constructor] Box(...) (line 7) -> ok (max_examples=30) strategies=[value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 1: [method] Box.describe_value(...) (line 10) -> ok (max_examples=30)
Plan 2: [method] Box.value_type_name(...) (line 28) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
