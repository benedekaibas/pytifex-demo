"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 6
Testable (strategies built): 4
Skipped (no strategies): 2
Bugs found: 1

Plan 0: [constructor] BaseConfig() (line 7) -> BUG FOUND (max_examples=30)
Plan 1: [method] BaseConfig.is_valid(...) (line 11) -> SKIPPED: cannot construct receiver BaseConfig
Plan 2: [method] BaseConfig.get_setting(...) (line 14) -> SKIPPED: cannot construct receiver BaseConfig
Plan 3: [function] config_factory(...) (line 18) -> ok (max_examples=30) strategies=[cache=bool -> booleans()]
Plan 4: [constructor] AppConfig() (line 33) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30), version=str -> text(max_size=30)]
Plan 5: [method] AppConfig.is_valid(...) (line 38) -> ok (max_examples=30)

Bugs:
  0: L7 [TypeError] BaseConfig() -> TypeError: Protocols cannot be instantiated
      test_cases_run=1, failing_args={}
"""
