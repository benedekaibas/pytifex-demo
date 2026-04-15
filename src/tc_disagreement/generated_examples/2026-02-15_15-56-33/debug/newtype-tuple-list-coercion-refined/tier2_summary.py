"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 0

Plan 0: [function] is_order_items_candidate(...) (line 6) -> ok (max_examples=30) strategies=[arg=Tuple -> lists(text(max_size=30), max_size=5).map(tuple)]
Plan 1: [function] process_and_refine_orders(...) (line 19) -> ok (max_examples=30) strategies=[raw_items_list=List -> lists(lists(text(max_size=30), max_size=5).map(tuple), max_size=5)]
Plan 2: [function] consume_order_items(...) (line 41) -> ok (max_examples=30) strategies=[orders=List -> lists(lists(text(max_size=30), max_size=5).map(tuple).map(OrderItems), max_si...]

No bugs found by Tier 2.
"""
