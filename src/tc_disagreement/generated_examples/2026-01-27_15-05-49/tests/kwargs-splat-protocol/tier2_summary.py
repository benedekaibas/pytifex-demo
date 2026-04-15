"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 6
Testable (strategies built): 2
Skipped (no strategies): 4
Bugs found: 0

Plan 0: [constructor] MinimalKwargProtocol() (line 4) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [method] MinimalKwargProtocol.keys(...) (line 5) -> SKIPPED: cannot construct receiver MinimalKwargProtocol
Plan 2: [constructor] CustomKwargSource(...) (line 11) -> ok (max_examples=30) strategies=[data=dict -> dictionaries(keys=text(max_size=30), values=integers(min_value=-1000, max_val...]
Plan 3: [method] CustomKwargSource.keys(...) (line 14) -> ok (max_examples=30)
Plan 4: [function] func_accepting_kwargs(...) (line 23) -> SKIPPED: could not resolve callable in live namespace
Plan 5: [function] test_protocol_splat(...) (line 26) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
