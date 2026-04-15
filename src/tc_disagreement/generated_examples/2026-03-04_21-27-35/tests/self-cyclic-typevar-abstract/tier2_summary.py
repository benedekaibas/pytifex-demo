"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 15
Testable (strategies built): 11
Skipped (no strategies): 4
Bugs found: 2

Plan 0: [constructor] ConcreteContainer() (line 6) -> ok (max_examples=30)
Plan 1: [constructor] ConcreteItem() (line 9) -> ok (max_examples=30)
Plan 2: [constructor] Container() (line 16) -> BUG FOUND (max_examples=30)
Plan 3: [method] Container.add_item(...) (line 18) -> SKIPPED: cannot construct receiver Container
Plan 4: [method] Container.get_first_item(...) (line 20) -> SKIPPED: could not resolve callable in live namespace
Plan 5: [constructor] Item() (line 22) -> BUG FOUND (max_examples=30)
Plan 6: [method] Item.get_parent_container(...) (line 24) -> SKIPPED: could not resolve callable in live namespace
Plan 7: [method] Item.to_container(...) (line 26) -> SKIPPED: could not resolve callable in live namespace
Plan 8: [constructor] MyItem(...) (line 30) -> ok (max_examples=30) strategies=[value=int -> integers(min_value=-1000, max_value=1000)]
Plan 9: [method] MyItem.set_parent(...) (line 34) -> ok (max_examples=30) strategies=[parent=MyContainer -> just(<__hypothesis_tier2__.MyContainer object at 0x7f5a5a2d7f50>)]
Plan 10: [method] MyItem.get_parent_container(...) (line 37) -> ok (max_examples=30)
Plan 11: [method] MyItem.to_container(...) (line 41) -> ok (max_examples=30)
Plan 12: [constructor] MyContainer(...) (line 45) -> ok (max_examples=30)
Plan 13: [method] MyContainer.add_item(...) (line 48) -> ok (max_examples=30) strategies=[item=MyItem -> build_instance()]
Plan 14: [method] MyContainer.get_first_item(...) (line 53) -> ok (max_examples=30)

Bugs:
  0: L16 [TypeError] Container() -> TypeError: Can't instantiate abstract class Container without an implementation for abstract methods 'add_item', 'get_first_item'
      test_cases_run=1, failing_args={}
  1: L22 [TypeError] Item() -> TypeError: Can't instantiate abstract class Item without an implementation for abstract methods 'get_parent_container', 'to_container'
      test_cases_run=1, failing_args={}
"""
