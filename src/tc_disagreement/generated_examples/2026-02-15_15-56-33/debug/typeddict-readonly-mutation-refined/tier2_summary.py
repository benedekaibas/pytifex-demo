"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 2
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [constructor] Configurable() (line 9) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] MyConfig() (line 15) -> SKIPPED: could not resolve callable in live namespace
Plan 2: [function] add_setting_func(...) (line 21) -> ok (max_examples=30) strategies=[cfg_dict=Configurable -> build_td(), setting_name=str -> text(max_size=30)]
Plan 3: [function] process_configurable(...) (line 29) -> ok (max_examples=30) strategies=[cfg=Configurable -> build_td()]

No bugs found by Tier 2.
"""
