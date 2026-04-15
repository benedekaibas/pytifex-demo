"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 10
Testable (strategies built): 5
Skipped (no strategies): 5
Bugs found: 0

Plan 0: [constructor] TaskResultProcessor() (line 7) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [method] TaskResultProcessor.process_result(...) (line 8) -> SKIPPED: cannot construct receiver TaskResultProcessor
Plan 2: [constructor] MyStringProcessor() (line 10) -> ok (max_examples=30)
Plan 3: [method] MyStringProcessor.process_result(...) (line 11) -> ok (max_examples=30) strategies=[task=Task -> from_type(_asyncio.Task[str]), metadata=str -> text(max_size=30)]
Plan 4: [constructor] MyIntProcessor() (line 14) -> ok (max_examples=30)
Plan 5: [method] MyIntProcessor.process_result(...) (line 15) -> ok (max_examples=30) strategies=[task=Task -> from_type(_asyncio.Task[int]), metadata=str -> text(max_size=30)]
Plan 6: [function] some_int_task(...) (line 18) -> SKIPPED: could not resolve callable in live namespace
Plan 7: [function] some_str_task(...) (line 22) -> SKIPPED: could not resolve callable in live namespace
Plan 8: [function] wrap_processor_for_callback(...) (line 26) -> ok (max_examples=30) strategies=[processor=TaskResultProcessor -> from_type(__hypothesis_tier2__.TaskResultProcessor[T])]
Plan 9: [function] main(...) (line 31) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
