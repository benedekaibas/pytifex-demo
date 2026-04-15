"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 4
Skipped (no strategies): 0
Bugs found: 1

Plan 0: [constructor] MyContainer() (line 14) -> BUG FOUND (max_examples=30) strategies=[iterable=_empty -> one_of(integers(), text(max_size=20), booleans())]
Plan 1: [function] MyContainer.contains_int(...) (line 16) -> ok (max_examples=30) strategies=[item=object -> just(<object object at 0x701ce034a180>)]
Plan 2: [function] MyContainer.contains_str(...) (line 21) -> ok (max_examples=30) strategies=[item=object -> just(<object object at 0x701ce034a230>)]
Plan 3: [function] process_item_with_class_method(...) (line 25) -> ok (max_examples=30) strategies=[item=Union -> one_of(integers(min_value=-1000, max_value=1000), text(max_size=30), floats(m...]

Bugs:
  0: L14 [TypeError] MyContainer() -> TypeError: list() takes no keyword arguments
      test_cases_run=50, failing_args={'iterable': 0}
"""
