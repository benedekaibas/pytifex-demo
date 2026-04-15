"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 8
Testable (strategies built): 6
Skipped (no strategies): 2
Bugs found: 1

Plan 0: [constructor] AbstractFactory() (line 6) -> BUG FOUND (max_examples=30)
Plan 1: [method] AbstractFactory.create(...) (line 8) -> SKIPPED: cannot construct receiver AbstractFactory
Plan 2: [method] AbstractFactory.register_type(...) (line 12) -> SKIPPED: cannot construct receiver AbstractFactory
Plan 3: [constructor] BasicFactory(...) (line 18) -> ok (max_examples=30)
Plan 4: [method] BasicFactory._get_base_factory_instance(...) (line 22) -> ok (max_examples=30)
Plan 5: [method] BasicFactory.create(...) (line 25) -> ok (max_examples=30)
Plan 6: [method] BasicFactory.register_type(...) (line 30) -> ok (max_examples=30) strategies=[key=str -> text(max_size=30), value=str -> text(max_size=30)]
Plan 7: [constructor] ExtendedFactory(...) (line 35) -> ok (max_examples=30) strategies=[prefix=str -> text(max_size=30)]

Bugs:
  0: L6 [TypeError] AbstractFactory() -> TypeError: Can't instantiate abstract class AbstractFactory without an implementation for abstract methods 'create', 'register_type'
      test_cases_run=1, failing_args={}
"""
