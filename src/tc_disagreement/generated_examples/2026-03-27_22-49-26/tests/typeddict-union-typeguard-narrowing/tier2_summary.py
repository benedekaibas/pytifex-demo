"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 5
Testable (strategies built): 1
Skipped (no strategies): 4
Bugs found: 0

Plan 0: [constructor] RequestBase() (line 3) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] GetRequest() (line 6) -> SKIPPED: could not resolve callable in live namespace
Plan 2: [constructor] PostRequest() (line 9) -> SKIPPED: could not resolve callable in live namespace
Plan 3: [function] is_post_request_with_body(...) (line 17) -> ok (max_examples=30) strategies=[req=Union -> one_of(build_td(), build_td())]
Plan 4: [function] process_request(...) (line 20) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
