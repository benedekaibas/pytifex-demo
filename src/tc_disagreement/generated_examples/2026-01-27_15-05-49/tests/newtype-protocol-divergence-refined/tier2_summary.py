"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 2
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [constructor] HasValue() (line 4) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] PriceItem(...) (line 8) -> ok (max_examples=30) strategies=[value=float -> floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)]
Plan 2: [function] get_item_value(...) (line 19) -> SKIPPED: no strategy for param 'item' (hint=<class '__hypothesis_tier2__.HasValue'>)
Plan 3: [function] compare_money_in_list(...) (line 23) -> ok (max_examples=30) strategies=[items=List -> lists(build_instance().map(Money), max_size=5)]

No bugs found by Tier 2.
"""
