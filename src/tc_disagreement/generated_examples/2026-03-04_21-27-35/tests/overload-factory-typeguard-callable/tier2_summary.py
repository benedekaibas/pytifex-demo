"""
Hypothesis Tier 2 — Signature-Driven Property Test Summary

Definitions found: 8
Testable (strategies built): 4
Skipped (no strategies): 4
Bugs found: 0

Plan 0: [constructor] Widget(...) (line 5) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30)]
Plan 1: [constructor] SpecialWidget(...) (line 9) -> ok (max_examples=30) strategies=[name=str -> text(max_size=30), code=int -> integers(min_value=-1000, max_value=1000)]
Plan 2: [constructor] WidgetFactory() (line 15) -> ok (max_examples=30)
Plan 3: [function] WidgetFactory.create(...) (line 18) -> SKIPPED: could not resolve callable in live namespace
Plan 4: [function] WidgetFactory.create(...) (line 21) -> SKIPPED: could not resolve callable in live namespace
Plan 5: [function] WidgetFactory.create(...) (line 24) -> SKIPPED: could not resolve callable in live namespace
Plan 6: [function] WidgetFactory.create(...) (line 26) -> SKIPPED: could not resolve callable in live namespace
Plan 7: [function] process_widgets(...) (line 42) -> ok (max_examples=30) strategies=[widgets=list -> lists(build_instance(), max_size=5)]

No bugs found by Tier 2.
"""
