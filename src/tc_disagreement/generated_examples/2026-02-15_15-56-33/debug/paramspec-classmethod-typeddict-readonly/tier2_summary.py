"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 2
Skipped (no strategies): 2
Bugs found: 1

Plan 0: [constructor] ItemProps() (line 12) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [function] log_classmethod_args(...) (line 19) -> SKIPPED: no strategy for param 'func' (hint=typing.Callable[typing.Concatenate[C_cls, P_func], R_ret])
Plan 2: [constructor] InventoryManager() (line 27) -> ok (max_examples=30)
Plan 3: [function] InventoryManager.add_item(...) (line 30) -> BUG FOUND (max_examples=30)

Bugs:
  0: L30 [TypeError] InventoryManager.add_item(...) -> TypeError: InventoryManager.add_item() missing 1 required positional argument: 'item_data'
      test_cases_run=1, failing_args={}
"""
