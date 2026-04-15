"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 11
Testable (strategies built): 10
Skipped (no strategies): 1
Bugs found: 3

Plan 0: [function] all_instances_of(...) (line 7) -> BUG FOUND (max_examples=30) strategies=[items=List -> lists(one_of(integers(), text(max_size=10), booleans()), max_size=5), cls=type -> sampled_from([TypeVar, Protocol, Animal, Dog, Cat, Barkable, RealDog, FakeDog])]
Plan 1: [constructor] Animal() (line 15) -> ok (max_examples=30)
Plan 2: [constructor] Dog() (line 16) -> ok (max_examples=30)
Plan 3: [constructor] Cat() (line 17) -> ok (max_examples=30)
Plan 4: [constructor] Barkable() (line 20) -> BUG FOUND (max_examples=30)
Plan 5: [method] Barkable.bark(...) (line 21) -> SKIPPED: cannot construct receiver Barkable
Plan 6: [constructor] RealDog() (line 23) -> ok (max_examples=30)
Plan 7: [method] RealDog.bark(...) (line 24) -> ok (max_examples=30)
Plan 8: [constructor] FakeDog() (line 27) -> ok (max_examples=30)
Plan 9: [method] FakeDog.bark(...) (line 28) -> ok (max_examples=30)
Plan 10: [function] process_animals(...) (line 32) -> BUG FOUND (max_examples=30) strategies=[animals=List -> lists(one_of(just(<__hypothesis_tier2__.Animal object at 0x760561b5f6b0>), te...]

Bugs:
  0: L7 [TypeError] all_instances_of(...) -> TypeError: Instance and class checks can only be used with @runtime_checkable protocols
      test_cases_run=17, failing_args={'items': ['\x870®', -2008892262, False], 'cls': <class '__hypothesis_tier2__.Barkable'>}
  1: L20 [TypeError] Barkable() -> TypeError: Protocols cannot be instantiated
      test_cases_run=1, failing_args={}
  2: L32 [TypeError] process_animals(...) -> TypeError: Instance and class checks can only be used with @runtime_checkable protocols
      test_cases_run=11, failing_args={'animals': [<__hypothesis_tier2__.Animal object at 0x760561b5f6b0>]}
"""
