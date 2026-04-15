"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 4
Testable (strategies built): 3
Skipped (no strategies): 1
Bugs found: 0

Plan 0: [constructor] Foo(...) (line 11) -> ok (max_examples=30) strategies=[value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 1: [constructor] Bar(...) (line 16) -> ok (max_examples=30) strategies=[value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 2: [function] is_foo_literal_string_one(...) (line 20) -> SKIPPED: no strategy for param 'val' (hint=__hypothesis_tier2__.Foo[typing.Any])
Plan 3: [function] process_union_data(...) (line 24) -> ok (max_examples=30) strategies=[data=Union -> sampled_from(['raw', 'other_raw'])]

No bugs found by Tier 2.
"""
