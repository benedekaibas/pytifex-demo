"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 0

Plan 0: [function] is_list_of_user_ids(...) (line 9) -> ok (max_examples=30) strategies=[data=List -> lists(one_of(integers(), text(max_size=10), booleans()), max_size=5)]
Plan 1: [function] is_list_of_product_ids(...) (line 14) -> ok (max_examples=30) strategies=[data=List -> lists(one_of(integers(), text(max_size=10), booleans()), max_size=5)]
Plan 2: [function] process_id_list(...) (line 19) -> ok (max_examples=30) strategies=[input_list=List -> lists(one_of(text(max_size=30).map(UserID), integers(min_value=-1000, max_val...]

No bugs found by Tier 2.
"""
