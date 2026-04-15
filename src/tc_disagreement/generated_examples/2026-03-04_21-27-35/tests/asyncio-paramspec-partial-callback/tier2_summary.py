"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 5
Testable (strategies built): 3
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [function] my_long_running_task(...) (line 9) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] TaskReporter(...) (line 14) -> ok (max_examples=30) strategies=[prefix=str -> text(max_size=30)]
Plan 2: [method] TaskReporter.report_done(...) (line 17) -> ok (max_examples=30) strategies=[task=Task -> from_type(_asyncio.Task[typing.Any]), extra_msg=str -> text(max_size=30)]
Plan 3: [method] TaskReporter.report_error(...) (line 20) -> ok (max_examples=30) strategies=[task=Task -> from_type(_asyncio.Task[typing.Any]), error_detail=str -> text(max_size=30)]
Plan 4: [function] main(...) (line 24) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
