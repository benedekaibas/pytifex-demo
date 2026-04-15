"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 6
Testable (strategies built): 4
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [constructor] Configurable() (line 4) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [function] Configurable.load_config(...) (line 9) -> ok (max_examples=30)
Plan 2: [method] Configurable.get_setting(...) (line 11) -> SKIPPED: cannot construct receiver Configurable
Plan 3: [constructor] MyConfigLoader() (line 13) -> ok (max_examples=30)
Plan 4: [function] MyConfigLoader.load_config(...) (line 18) -> ok (max_examples=30)
Plan 5: [method] MyConfigLoader.get_setting(...) (line 24) -> ok (max_examples=30) strategies=[key=str -> text(max_size=30)]

No bugs found by Tier 2.
"""
