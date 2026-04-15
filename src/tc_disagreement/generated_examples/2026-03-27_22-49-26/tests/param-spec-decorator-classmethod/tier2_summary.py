"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 5
Testable (strategies built): 4
Skipped (no strategies): 1
Bugs found: 0

Plan 0: [function] record_call(...) (line 7) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] ServiceManager(...) (line 18) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30)]
Plan 2: [function] ServiceManager.create_named_manager(...) (line 24) -> ok (max_examples=30) strategies=[base_name=str -> text(max_size=30), suffix=str -> text(max_size=30)]
Plan 3: [method] ServiceManager.shutdown(...) (line 29) -> ok (max_examples=30) strategies=[reason=str -> text(max_size=30)]
Plan 4: [function] ServiceManager.get_total_managers(...) (line 35) -> ok (max_examples=30)

No bugs found by Tier 2.
"""
