"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 13
Testable (strategies built): 9
Skipped (no strategies): 4
Bugs found: 0

Plan 0: [constructor] Operation() (line 6) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [method] Operation.perform(...) (line 7) -> SKIPPED: cannot construct receiver Operation
Plan 2: [method] Operation.get_description(...) (line 8) -> SKIPPED: cannot construct receiver Operation
Plan 3: [method] Operation.default_value(...) (line 9) -> SKIPPED: cannot construct receiver Operation
Plan 4: [constructor] IntOp() (line 11) -> ok (max_examples=30)
Plan 5: [method] IntOp.perform(...) (line 12) -> ok (max_examples=30)
Plan 6: [method] IntOp.get_description(...) (line 14) -> ok (max_examples=30)
Plan 7: [method] IntOp.default_value(...) (line 16) -> ok (max_examples=30)
Plan 8: [constructor] StrOp() (line 19) -> ok (max_examples=30)
Plan 9: [method] StrOp.perform(...) (line 20) -> ok (max_examples=30)
Plan 10: [method] StrOp.get_description(...) (line 22) -> ok (max_examples=30)
Plan 11: [method] StrOp.default_value(...) (line 24) -> ok (max_examples=30)
Plan 12: [function] process_operation_result(...) (line 27) -> ok (max_examples=30) strategies=[op=Operation -> from_type(__hypothesis_tier2__.Operation[T])]

No bugs found by Tier 2.
"""
