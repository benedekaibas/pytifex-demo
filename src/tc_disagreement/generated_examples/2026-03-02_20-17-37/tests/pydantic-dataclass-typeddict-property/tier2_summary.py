"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 5
Testable (strategies built): 1
Skipped (no strategies): 4
Bugs found: 0

Plan 0: [constructor] Metadata() (line 5) -> SKIPPED: could not resolve callable in live namespace
Plan 1: [constructor] ExtendedInfo() (line 10) -> SKIPPED: could not resolve callable in live namespace
Plan 2: [constructor] DataRecord() (line 15) -> ok (max_examples=30) strategies=[record_id=str -> text(max_size=30), value=int -> integers(min_value=-1000, max_value=1000), metadata=Metadata -> build_td(), extended_info=Union -> one_of(build_td(), just('not_available'))]
Plan 3: [method] DataRecord.record_tags(...) (line 22) -> SKIPPED: could not resolve callable in live namespace
Plan 4: [method] DataRecord.owner_email(...) (line 28) -> SKIPPED: could not resolve callable in live namespace

No bugs found by Tier 2.
"""
