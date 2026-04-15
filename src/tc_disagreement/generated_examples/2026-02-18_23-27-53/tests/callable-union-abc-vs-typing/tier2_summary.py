"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 0

Plan 0: [function] specific_int_to_str(...) (line 4) -> ok (max_examples=30) strategies=[x=int -> integers(min_value=-1000, max_value=1000)]
Plan 1: [function] specific_str_to_bool(...) (line 7) -> ok (max_examples=30) strategies=[x=str -> text(max_size=30)]
Plan 2: [function] process_callable_types_union(...) (line 13) -> ok (max_examples=30) strategies=[item=Union -> one_of(functions(like=lambda *a, **k: None, returns=text()), none())]

No bugs found by Tier 2.
"""
