"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 0

Plan 0: [function] process_int_metric(...) (line 18) -> ok (max_examples=30) strategies=[value=int -> integers(min_value=-1000, max_value=1000)]
Plan 1: [function] process_complex_metric_data(...) (line 21) -> ok (max_examples=30) strategies=[data=ComplexMetricAlias -> from_type(__hypothesis_tier2__.ComplexMetricAlias[str, float, [int], bool])]
Plan 2: [function] test_complex_typealiastype(...) (line 38) -> ok (max_examples=30)

No bugs found by Tier 2.
"""
