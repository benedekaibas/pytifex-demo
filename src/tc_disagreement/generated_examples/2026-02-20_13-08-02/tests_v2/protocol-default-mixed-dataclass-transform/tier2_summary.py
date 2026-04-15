"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 7
Testable (strategies built): 5
Skipped (no strategies): 2
Bugs found: 1

Plan 0: [constructor] BaseProcessor() (line 6) -> BUG FOUND (max_examples=30)
Plan 1: [method] BaseProcessor.process(...) (line 9) -> SKIPPED: cannot construct receiver BaseProcessor
Plan 2: [method] BaseProcessor.post_process(...) (line 13) -> SKIPPED: cannot construct receiver BaseProcessor
Plan 3: [function] processor_factory(...) (line 20) -> ok (max_examples=30) strategies=[enhance_process=bool -> booleans()]
Plan 4: [constructor] MyDataProcessor() (line 33) -> ok (max_examples=30) strategies=[data_source=str -> text(max_size=30), config_param=int -> integers(min_value=-1000, max_value=1000)]
Plan 5: [constructor] AnotherProcessor(...) (line 43) -> ok (max_examples=30) strategies=[data_source=str -> text(max_size=30), config_param=int -> integers(min_value=-1000, max_value=1000)]
Plan 6: [method] AnotherProcessor.process(...) (line 47) -> ok (max_examples=30) strategies=[item=Any -> one_of(integers(), text(max_size=10), booleans(), none())]

Bugs:
  0: L6 [TypeError] BaseProcessor() -> TypeError: Protocols cannot be instantiated
      test_cases_run=1, failing_args={}
"""
