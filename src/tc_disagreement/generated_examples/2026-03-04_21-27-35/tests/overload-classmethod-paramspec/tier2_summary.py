"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 8
Testable (strategies built): 5
Skipped (no strategies): 3
Bugs found: 0

Plan 0: [constructor] Factory() (line 8) -> ok (max_examples=30)
Plan 1: [function] Factory.register(...) (line 13) -> SKIPPED: could not resolve callable in live namespace
Plan 2: [function] Factory.register(...) (line 16) -> SKIPPED: could not resolve callable in live namespace
Plan 3: [function] Factory.register(...) (line 18) -> SKIPPED: could not resolve callable in live namespace
Plan 4: [function] Factory.create(...) (line 37) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30)]
Plan 5: [function] simple_function(...) (line 42) -> ok (max_examples=30) strategies=[a=int -> integers(min_value=-1000, max_value=1000), b=str -> text(max_size=30)]
Plan 6: [constructor] MyClass(...) (line 46) -> ok (max_examples=30) strategies=[x=int -> integers(min_value=-1000, max_value=1000)]
Plan 7: [method] MyClass.greet(...) (line 48) -> ok (max_examples=30)

No bugs found by Tier 2.
"""
