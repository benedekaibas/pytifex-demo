"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 0

Plan 0: [function] is_str_pair(...) (line 7) -> ok (max_examples=30) strategies=[val=Tuple -> tuples(one_of(integers(), text(max_size=10), booleans(), none()), one_of(inte...]
Plan 1: [function] is_int_bool_pair(...) (line 11) -> ok (max_examples=30) strategies=[val=Tuple -> tuples(one_of(integers(), text(max_size=10), booleans(), none()), one_of(inte...]
Plan 2: [function] process_item(...) (line 16) -> ok (max_examples=30) strategies=[item=Union -> one_of(tuples(integers(min_value=-1000, max_value=1000), booleans()), tuples(...]

No bugs found by Tier 2.
"""
