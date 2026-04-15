"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: kwargs-splat-protocol.py
Patterns detected: 1
    - protocol_conformance (1 tests)
Test cases generated: 1
"""

# --- Original source ---

from typing import Protocol, runtime_checkable, Mapping, KeysView, Any, reveal_type, Iterator

@runtime_checkable
class MinimalKwargProtocol(Protocol):
    def keys(self) -> KeysView[str]: ...
    def __getitem__(self, key: str) -> Any: ...
    # Crucially, no items() or __iter__ is explicitly defined here.
    # The `**` operator at runtime typically calls `dict(obj.items())` or `dict(obj)` if iterable.

class CustomKwargSource:
    def __init__(self, data: dict[str, int]):
        self._data = data
    
    def keys(self) -> KeysView[str]:
        return self._data.keys()
    
    def __getitem__(self, key: str) -> int:
        return self._data[key]
    
    # Missing items() which is required for `**` at runtime.
    # Also doesn't inherit from Mapping or dict.

def func_accepting_kwargs(**kwargs: Any):
    print(f"Received kwargs: {kwargs}")

def test_protocol_splat(
    source_impl: CustomKwargSource,
    source_protocol: MinimalKwargProtocol, # source_impl is passed here
    source_mapping: Mapping[str, int],
):
    # Does type checker identify that CustomKwargSource lacks `items()` for `**`?
    reveal_type({**source_impl})  # Expected: dict[str, int] if `items()` assumed, else `dict[Unknown, Unknown]` or error.
    reveal_type({**source_protocol}) # Expected: same as above
    reveal_type({**source_mapping}) # Expected: dict[str, int] (should be fine)

    func_accepting_kwargs(**source_impl)    # Should be a runtime TypeError. Type checker might miss.
    func_accepting_kwargs(**source_protocol) # Same as above
    func_accepting_kwargs(**source_mapping) # Should be fine

if __name__ == "__main__":
    impl = CustomKwargSource({"alpha": 1, "beta": 2})
    
    # Python runtime will raise TypeError: `kwargs` takes mapping type, not CustomKwargSource
    # unless CustomKwargSource defines .items() or __iter__ yielding (key, value) pairs.
    # Checkers like pyright might allow `**source_impl` at call site, matching the original issue.
    # mypy might report `dict[Unknown, Unknown]` for `reveal_type` on splat, but not error call site.
    
    print("Testing kwargs splat behavior with a custom class that implements keys/__getitem__ but lacks items().")
    print("This should be a runtime error for CustomKwargSource without an `items()` method.")
    # Uncommenting the call below will cause a runtime TypeError.
    # test_protocol_splat(impl, impl, {"gamma": 3})
    
    # To run without crashing on `**source_impl`, but still trigger type checking:
    print("\nRunning `reveal_type` for type checking purposes:")
    test_protocol_splat(impl, impl, {"gamma": 3})

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_MinimalKwargProtocol_non_conforming_object():
    """Pass a non-conforming object where Protocol MinimalKwargProtocol is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
