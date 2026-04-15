"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 9
Testable (strategies built): 8
Skipped (no strategies): 1
Bugs found: 0

Plan 0: [constructor] Vehicle() (line 5) -> ok (max_examples=30)
Plan 1: [method] Vehicle.drive(...) (line 6) -> ok (max_examples=30)
Plan 2: [constructor] Car() (line 9) -> ok (max_examples=30)
Plan 3: [method] Car.honk(...) (line 10) -> ok (max_examples=30)
Plan 4: [method] Car.drive(...) (line 12) -> ok (max_examples=30)
Plan 5: [constructor] Bike() (line 15) -> ok (max_examples=30)
Plan 6: [method] Bike.pedal(...) (line 16) -> ok (max_examples=30)
Plan 7: [function] all_are_specific_vehicles(...) (line 42) -> SKIPPED: could not resolve callable in live namespace
Plan 8: [function] process_vehicles(...) (line 52) -> ok (max_examples=30) strategies=[vehicles=List -> lists(one_of(text(max_size=30), just(<__hypothesis_tier2__.Vehicle object at ...]

No bugs found by Tier 2.
"""
