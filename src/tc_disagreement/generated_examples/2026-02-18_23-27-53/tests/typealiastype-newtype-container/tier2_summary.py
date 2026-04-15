"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 2
Testable (strategies built): 2
Skipped (no strategies): 0
Bugs found: 1

Plan 0: [function] process_user_ids(...) (line 11) -> ok (max_examples=30) strategies=[ids=IDList -> lists(integers())]
Plan 1: [function] test_newtype_typealiastype(...) (line 21) -> BUG FOUND (max_examples=30)

Bugs:
  0: L21 [TypeError] test_newtype_typealiastype(...) -> TypeError: 'typing.TypeAliasType' object is not callable
      test_cases_run=1, failing_args={}
"""
