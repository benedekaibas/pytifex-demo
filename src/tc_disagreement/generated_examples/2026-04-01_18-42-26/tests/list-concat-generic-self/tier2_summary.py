"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 0

Plan 0: [constructor] BaseContainer(...) (line 6) -> ok (max_examples=30) strategies=[data=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 1: [constructor] SpecializedContainer() (line 9) -> ok (max_examples=30) strategies=[data=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 2: [function] handle_containers(...) (line 12) -> ok (max_examples=30) strategies=[containers=list -> lists(from_type(__hypothesis_tier2__.BaseContainer[str]), max_size=5)]

No bugs found by Tier 2.
"""
