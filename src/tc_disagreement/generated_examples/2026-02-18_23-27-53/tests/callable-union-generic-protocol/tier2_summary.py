"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 5
Testable (strategies built): 4
Skipped (no strategies): 1
Bugs found: 1

Plan 0: [constructor] Converter() (line 6) -> BUG FOUND (max_examples=30)
Plan 1: [method] Converter.convert_default(...) (line 8) -> SKIPPED: cannot construct receiver Converter
Plan 2: [constructor] IntConverter() (line 10) -> ok (max_examples=30)
Plan 3: [method] IntConverter.convert_default(...) (line 13) -> ok (max_examples=30)
Plan 4: [function] handle_mixed_callable(...) (line 16) -> ok (max_examples=30) strategies=[cb=Union -> one_of(from_type(typing.Callable[..., typing.Any]), from_type(__hypothesis_ti...]

Bugs:
  0: L6 [TypeError] Converter() -> TypeError: Protocols cannot be instantiated
      test_cases_run=1, failing_args={}
"""
