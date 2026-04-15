"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 6
Testable (strategies built): 4
Skipped (no strategies): 2
Bugs found: 0

Plan 0: [constructor] Node(...) (line 7) -> ok (max_examples=30) strategies=[next_node=Optional -> one_of(from_type(__hypothesis_tier2__.Node[T]), none()), value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 1: [method] Node.get_next_or_default(...) (line 13) -> ok (max_examples=30) strategies=[default_val=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 2: [method] Node.get_value(...) (line 36) -> SKIPPED: could not resolve callable in live namespace
Plan 3: [constructor] SpecialNode(...) (line 41) -> ok (max_examples=30) strategies=[next_node=Optional -> one_of(from_type(__hypothesis_tier2__.Node[T]), none()), metadata=str -> text(max_size=30), value=TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())]
Plan 4: [method] SpecialNode.get_metadata(...) (line 45) -> ok (max_examples=30)
Plan 5: [function] process_nodes_in_loop(...) (line 48) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
