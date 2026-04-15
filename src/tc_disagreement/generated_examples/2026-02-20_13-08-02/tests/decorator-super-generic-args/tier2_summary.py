"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 5
Testable (strategies built): 5
Skipped (no strategies): 0
Bugs found: 1

Plan 0: [function] trace_method(...) (line 7) -> ok (max_examples=30) strategies=[func=Callable -> from_type(typing.Callable[P, R])]
Plan 1: [constructor] Base() (line 14) -> ok (max_examples=30)
Plan 2: [method] Base.greet(...) (line 15) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30)]
Plan 3: [constructor] Derived() (line 18) -> ok (max_examples=30)
Plan 4: [method] Derived.greet(...) (line 20) -> BUG FOUND (max_examples=30)

Bugs:
  0: L20 [TypeError] Derived.greet(...) -> TypeError: Derived.greet() missing 1 required positional argument: 'name'
      test_cases_run=2, failing_args={}
"""
