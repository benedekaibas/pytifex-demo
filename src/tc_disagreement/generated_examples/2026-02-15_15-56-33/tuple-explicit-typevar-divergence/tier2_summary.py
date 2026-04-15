"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 3
Testable (strategies built): 3
Skipped (no strategies): 0
Bugs found: 1

Plan 0: [function] process_empty_tuple_dict(...) (line 11) -> BUG FOUND (max_examples=30) strategies=[data=Dict -> dictionaries(keys=just(()), values=one_of(integers(), text(max_size=10), bool...]
Plan 1: [function] process_list_of_fixed_tuples(...) (line 17) -> ok (max_examples=30) strategies=[data=List -> lists(tuples(one_of(integers(), text(max_size=10), booleans()), just(())), ma...]
Plan 2: [function] process_non_empty_tuple(...) (line 22) -> ok (max_examples=30) strategies=[data=Tuple -> lists(one_of(integers(), text(max_size=10), booleans()), max_size=5).map(tuple)]

Bugs:
  0: L11 [KeyError] process_empty_tuple_dict(...) -> KeyError: ()
      test_cases_run=12, failing_args={'data': {}}
"""
