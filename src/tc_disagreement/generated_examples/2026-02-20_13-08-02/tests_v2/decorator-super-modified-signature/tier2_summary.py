"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 5
Testable (strategies built): 4
Skipped (no strategies): 1
Bugs found: 1

Plan 0: [function] inject_context(...) (line 8) -> SKIPPED: no strategy for param 'func' (hint=typing.Callable[typing.Concatenate[~_Self, P], R])
Plan 1: [constructor] Base() (line 14) -> ok (max_examples=30)
Plan 2: [method] Base.process_data(...) (line 15) -> ok (max_examples=30) strategies=[data=int -> integers(min_value=-1000, max_value=1000)]
Plan 3: [constructor] Derived() (line 18) -> ok (max_examples=30)
Plan 4: [method] Derived.process_data(...) (line 20) -> BUG FOUND (max_examples=30) strategies=[context=str -> text(max_size=30)]

Bugs:
  0: L20 [TypeError] Derived.process_data(...) -> TypeError: Derived.process_data() missing 2 required positional arguments: 'context' and 'data'
      test_cases_run=91, failing_args={'context': ''}
"""
