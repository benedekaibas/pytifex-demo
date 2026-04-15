"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 6
Testable (strategies built): 4
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [function] calculate_sum(...) (line 8) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] ResultHandler(...) (line 13) -> ok (max_examples=30) strategies=[tag=str -> text(max_size=30)]
Plan 2: [method] ResultHandler.handle_result(...) (line 16) -> ok (max_examples=30) strategies=[task=Task -> from_type(_asyncio.Task[typing.Any])]
Plan 3: [method] ResultHandler.handle_specific(...) (line 22) -> ok (max_examples=30) strategies=[task=Task -> from_type(_asyncio.Task[int])]
Plan 4: [function] generic_callback_wrapper(...) (line 28) -> ok (max_examples=30) strategies=[handler=Callable -> from_type(typing.Callable[typing.Concatenate[_asyncio.Task[typing.Any], ~P], ...]
Plan 5: [function] main(...) (line 48) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
