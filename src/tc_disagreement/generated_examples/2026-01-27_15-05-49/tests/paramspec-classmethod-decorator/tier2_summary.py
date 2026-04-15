"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 6
Testable (strategies built): 4
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [function] class_method_logger(...) (line 8) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] BaseProcessor(...) (line 22) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30)]
Plan 2: [function] BaseProcessor.create_named_instance(...) (line 28) -> SKIPPED: could not resolve callable in live namespace
Plan 3: [function] BaseProcessor.get_total_instances(...) (line 38) -> ok (max_examples=30)
Plan 4: [constructor] MySpecialProcessor(...) (line 42) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30)]
Plan 5: [method] MySpecialProcessor.get_special_id(...) (line 46) -> ok (max_examples=30)

No bugs found by Tier 2.
"""
