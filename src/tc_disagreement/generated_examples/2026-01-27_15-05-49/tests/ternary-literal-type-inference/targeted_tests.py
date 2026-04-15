"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: ternary-literal-type-inference.py
Patterns detected: 1
    - main_block_replay (3 tests)
Test cases generated: 3
"""

# --- Original source ---

from typing import Literal, Union, reveal_type

def get_db_port(env_mode: Literal["dev", "test", "prod"]) -> Union[Literal[5432], Literal[1234]]:
    """Returns a database port based on environment mode."""
    port = 5432 if env_mode == "dev" or env_mode == "test" else 1234
    reveal_type(port) # Expected: Literal[5432] if "dev"|"test", else Literal[1234], overall Union[Literal[5432], Literal[1234]]
    return port

def connect_to_db(address: str, port: Union[Literal[5432], Literal[1234]]):
    reveal_type(port) # Expected: Union[Literal[5432], Literal[1234]]
    if port == 5432:
        print(f"Connecting to production/dev DB at {address}:{port}")
    else:
        print(f"Connecting to test/staging DB at {address}:{port}")

def configure_system(runtime_env_str: str):
    """
    This function takes a runtime string which cannot be narrowed by type checkers.
    The ternary condition `runtime_env_str == "production"` is dynamic.
    """
    db_connection_port = (
        get_db_port("prod") if runtime_env_str == "production" else get_db_port("test")
    )
    reveal_type(db_connection_port) # Expected: Union[Literal[1234], Literal[5432]] (the full union)

    # The type checker must correctly maintain the Union type for `db_connection_port`
    # because `runtime_env_str == "production"` cannot be resolved statically.
    connect_to_db("db.example.com", db_connection_port) # This should always pass.

    # Another subtle case: ternary affecting literal assigned to a class attribute
    class AppConfig:
        def __init__(self, debug_mode: Literal[True, False]):
            self.debug_mode = debug_mode

    app_debug_setting: Literal[True, False] = (
        True if runtime_env_str.startswith("dev") else False
    )
    reveal_type(app_debug_setting) # Expected: Union[Literal[True], Literal[False]]
    
    app = AppConfig(app_debug_setting) # This should be fine
    reveal_type(app.debug_mode) # Expected: Union[Literal[True], Literal[False]]

if __name__ == "__main__":
    print(f"Dev port: {get_db_port('dev')}")
    print(f"Prod port: {get_db_port('prod')}")

    print("\n--- Testing configure_system ---")
    configure_system("production")
    configure_system("development")
    configure_system("staging")

    print("\nExample demonstrating type inference with Literal in ternary expressions.")
    print("Checks if type checkers correctly handle ternary conditions based on runtime-only string values,")
    print("maintaining Union types where static narrowing is not possible.")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_main_call_configure_system__production__():
    """Execute main block call: configure_system('production')"""
    import traceback as _tb, sys as _sys
    try:
        configure_system('production')
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 48
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_configure_system__development__():
    """Execute main block call: configure_system('development')"""
    import traceback as _tb, sys as _sys
    try:
        configure_system('development')
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 49
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_configure_system__staging__():
    """Execute main block call: configure_system('staging')"""
    import traceback as _tb, sys as _sys
    try:
        configure_system('staging')
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 50
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
