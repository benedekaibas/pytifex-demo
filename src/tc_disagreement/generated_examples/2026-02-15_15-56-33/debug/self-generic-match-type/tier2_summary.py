"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 8
Testable (strategies built): 8
Skipped (no strategies): 0
Bugs found: 3

Plan 0: [constructor] Box(...) (line 11) -> ok (max_examples=30) strategies=[value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 1: [method] Box.copy(...) (line 14) -> ok (max_examples=30)
Plan 2: [method] Box.unwrap(...) (line 19) -> ok (max_examples=30)
Plan 3: [constructor] IntBox() (line 23) -> ok (max_examples=30) strategies=[value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 4: [method] IntBox.double(...) (line 24) -> ok (max_examples=30)
Plan 5: [constructor] StrBox() (line 28) -> ok (max_examples=30) strategies=[value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 6: [method] StrBox.upper(...) (line 29) -> BUG FOUND (max_examples=30)
Plan 7: [function] inspect_box_return(...) (line 33) -> BUG FOUND (max_examples=30) strategies=[box_instance=Union -> one_of(build_instance(), build_instance())]

Bugs:
  0: L29 [AttributeError] StrBox.upper(...) -> AttributeError: 'int' object has no attribute 'upper'
      test_cases_run=12, failing_args={}
  1: L29 [AttributeError] StrBox.upper(...) -> AttributeError: 'bool' object has no attribute 'upper'
      test_cases_run=12, failing_args={}
  2: L33 [TypeError] inspect_box_return(...) -> TypeError: type() accepts 0 positional sub-patterns (1 given)
      test_cases_run=44, failing_args={'box_instance': <__hypothesis_tier2__.IntBox object at 0x76f42415b440>}
"""
