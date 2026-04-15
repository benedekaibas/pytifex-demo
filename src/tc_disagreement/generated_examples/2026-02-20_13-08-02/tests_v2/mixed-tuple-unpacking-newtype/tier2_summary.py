"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 1
Testable (strategies built): 1
Skipped (no strategies): 0
Bugs found: 1

Plan 0: [function] process_complex_packet(...) (line 7) -> BUG FOUND (max_examples=30) strategies=[packet=Tuple -> just(())]

Bugs:
  0: L7 [ValueError] process_complex_packet(...) -> ValueError: not enough values to unpack (expected at least 2, got 0)
      test_cases_run=2, failing_args={'packet': ()}
"""
