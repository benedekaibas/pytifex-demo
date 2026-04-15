"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 2
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [constructor] Inventory() (line 8) -> ok (max_examples=30) strategies=[dict=_empty -> one_of(integers(), text(max_size=20), booleans())]
Plan 1: [method] Inventory.add_item(...) (line 9) -> SKIPPED: cannot construct receiver Inventory
Plan 2: [constructor] CategorizedInventory() (line 13) -> ok (max_examples=30) strategies=[dict=_empty -> one_of(integers(), text(max_size=20), booleans())]
Plan 3: [method] CategorizedInventory.add_item(...) (line 18) -> SKIPPED: cannot construct receiver CategorizedInventory

No bugs found by Tier 2.
"""
