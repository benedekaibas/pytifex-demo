"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 0

Plan 0: [function] class_builder(...) (line 11) -> ok (max_examples=30) strategies=[frozen=bool -> booleans(), extra_init=bool -> booleans()]
Plan 1: [constructor] ImmutableData() (line 25) -> ok (max_examples=30) strategies=[id=int -> integers(min_value=-1000, max_value=1000), name=str -> text(max_size=30)]
Plan 2: [constructor] CustomInitData() (line 30) -> ok (max_examples=30)

No bugs found by Tier 2.
"""
