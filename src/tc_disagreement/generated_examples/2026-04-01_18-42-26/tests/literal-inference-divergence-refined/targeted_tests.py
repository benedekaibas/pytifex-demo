"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: literal-inference-divergence-refined.py
Patterns detected: 1
    - main_block_replay (2 tests)
Test cases generated: 2
"""

# --- Original source ---

from typing import Literal

class AppConfig:
    # DEFAULT_MODE is no longer explicitly typed as 'str'.
    # Its runtime value is 'production'.
    # Type checkers will now need to infer its type.
    DEFAULT_MODE = 'production'

# Define a Literal type for allowed modes.
Mode = Literal['production', 'development', 'staging']

def set_app_mode(mode: Mode) -> None:
    print(f"App mode set to: {mode}")

if __name__ == "__main__":
    # Case 1: Passing a direct literal value.
    # This universally passes as 'production' is a valid literal in Mode.
    set_app_mode('production')

    # Case 2: Passing a variable whose type is inferred.
    # This is the intended point of divergence:
    # - Mypy and Pyright are known for strong literal inference. They are likely
    #   to infer `AppConfig.DEFAULT_MODE` as `Literal['production']`,
    #   which is compatible with `Mode`. This would lead to a PASS for them.
    # - Other type checkers (like Zuban or Ty) might be less aggressive
    #   with literal inference for untyped class attributes. They could
    #   potentially infer the type as `str`, which is not assignable to `Mode`.
    #   If they infer `str`, this would lead to an ERROR for them.
    set_app_mode(AppConfig.DEFAULT_MODE)

    # Case 3: Passing a string literal that is NOT in Mode.
    # This should universally fail for all type checkers.
    # set_app_mode('invalid_mode') # Uncomment to confirm this error

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_main_call_set_app_mode__production__():
    """Execute main block call: set_app_mode('production')"""
    import traceback as _tb, sys as _sys
    try:
        set_app_mode('production')
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 18
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_set_app_mode_AppConfig_DEFAULT_MODE_():
    """Execute main block call: set_app_mode(AppConfig.DEFAULT_MODE)"""
    import traceback as _tb, sys as _sys
    try:
        set_app_mode(AppConfig.DEFAULT_MODE)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 29
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


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
