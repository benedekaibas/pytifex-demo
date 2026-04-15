"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 4
Skipped (no strategies): 0
Bugs found: 1

Plan 0: [function] typeis_wrapper(...) (line 7) -> ok (max_examples=30) strategies=[func=Callable -> from_type(typing.Callable[~P, typing_extensions.TypeIs[R]])]
Plan 1: [constructor] Validator() (line 15) -> ok (max_examples=30)
Plan 2: [method] Validator.is_list_of_ints(...) (line 17) -> BUG FOUND (max_examples=30)
Plan 3: [function] check_decorated_typeis(...) (line 23) -> ok (max_examples=30) strategies=[data=object -> just(<object object at 0x701ce034a0c0>)]

Bugs:
  0: L17 [TypeError] Validator.is_list_of_ints(...) -> TypeError: Validator.is_list_of_ints() missing 1 required positional argument: 'x'
      test_cases_run=2, failing_args={}
"""
