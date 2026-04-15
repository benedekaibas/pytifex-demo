"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 8
Testable (strategies built): 7
Skipped (no strategies): 1
Bugs found: 0

Plan 0: [constructor] BaseThing() (line 5) -> ok (max_examples=30)
Plan 1: [method] BaseThing.get_info(...) (line 6) -> ok (max_examples=30)
Plan 2: [constructor] SpecialThing() (line 9) -> ok (max_examples=30)
Plan 3: [method] SpecialThing.get_special_info(...) (line 10) -> ok (max_examples=30)
Plan 4: [method] SpecialThing.get_info(...) (line 12) -> ok (max_examples=30)
Plan 5: [function] is_special(...) (line 15) -> ok (max_examples=30) strategies=[val=Union -> one_of(one_of(integers(), text(max_size=10), booleans()), just(<__hypothesis_...]
Plan 6: [function] process_special(...) (line 22) -> ok (max_examples=30) strategies=[s=SpecialThing -> just(<__hypothesis_tier2__.SpecialThing object at 0x79a817920680>)]
Plan 7: [function] get_action_lambda(...) (line 25) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
