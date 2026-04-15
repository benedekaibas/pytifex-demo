"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 10
Testable (strategies built): 5
Skipped (no strategies): 5
Bugs found: 1

Plan 0: [constructor] Validatable() (line 10) -> BUG FOUND (max_examples=30)
Plan 1: [method] Validatable.value(...) (line 12) -> SKIPPED: could not resolve callable in live namespace
Plan 2: [method] Validatable.is_valid(...) (line 16) -> SKIPPED: cannot construct receiver Validatable
Plan 3: [constructor] User(...) (line 23) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30), is_active=bool -> booleans()]
Plan 4: [method] User.value(...) (line 28) -> SKIPPED: could not resolve callable in live namespace
Plan 5: [method] User.is_valid(...) (line 32) -> ok (max_examples=30)
Plan 6: [constructor] Product(...) (line 38) -> ok (max_examples=30) strategies=[price=float -> floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False), in_stock=int -> integers(min_value=-1000, max_value=1000)]
Plan 7: [method] Product.value(...) (line 43) -> SKIPPED: could not resolve callable in live namespace
Plan 8: [method] Product.is_valid(...) (line 47) -> ok (max_examples=30)
Plan 9: [function] process_entity(...) (line 52) -> SKIPPED: no strategy for param 'entity' (hint=__hypothesis_tier2__.Validatable[typing.Union[str, float]])

Bugs:
  0: L10 [TypeError] Validatable() -> TypeError: Protocols cannot be instantiated
      test_cases_run=1, failing_args={}
"""
