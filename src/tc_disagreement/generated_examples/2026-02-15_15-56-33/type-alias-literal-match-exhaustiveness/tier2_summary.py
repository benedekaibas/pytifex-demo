"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 3
Skipped (no strategies): 1
Bugs found: 0

Plan 0: [constructor] Success(...) (line 9) -> ok (max_examples=30) strategies=[value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 1: [constructor] Failure(...) (line 13) -> ok (max_examples=30) strategies=[error=str -> text(max_size=30)]
Plan 2: [function] handle_result(...) (line 27) -> SKIPPED: no strategy for param 'res' (hint=Result[typing.Dict[str, typing.Any]])
Plan 3: [function] classify_id(...) (line 48) -> ok (max_examples=30) strategies=[identifier=SimpleID -> sampled_from(['End', 'Middle', 'Start']) [from_type fallback]]

No bugs found by Tier 2.
"""
