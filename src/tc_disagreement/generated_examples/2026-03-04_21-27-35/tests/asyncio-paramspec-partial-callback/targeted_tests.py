"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: asyncio-paramspec-partial-callback.py
Patterns detected: 1
    - main_block_replay (1 tests)
Test cases generated: 1
"""

# --- Original source ---

import asyncio
from typing import ParamSpec, Callable, Any, TypeVar
from functools import partial
from typing_extensions import reveal_type

P = ParamSpec("P")
R = TypeVar("R")

async def my_long_running_task(param1: str, param2: int) -> str:
    await asyncio.sleep(0.01)
    return f"Task done: {param1}-{param2}"

class TaskReporter:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def report_done(self, task: asyncio.Task[Any], extra_msg: str = "") -> None:
        print(f"{self.prefix} - Task {task.get_name()} completed. Result: {task.result()}. {extra_msg}")

    def report_error(self, task: asyncio.Task[Any], error_detail: str) -> None:
        if task.exception():
            print(f"ERROR: {self.prefix} - Task {task.get_name()} failed with {task.exception()}. Detail: {error_detail}")

async def main():
    reporter = TaskReporter("Main")

    task1 = asyncio.create_task(my_long_running_task("a", 1), name="task1")
    task1.add_done_callback(reporter.report_done)

    task2 = asyncio.create_task(my_long_running_task("b", 2), name="task2")
    callback_with_extra = partial(reporter.report_done, extra_msg="Handled by partial")
    reveal_type(callback_with_extra) # Expected: Callable[[asyncio.Task[Any]], None]
    task2.add_done_callback(callback_with_extra)

    task3 = asyncio.create_task(my_long_running_task("c", 3), name="task3")
    # This partial expects no arguments, as it tries to bind 'task' implicitly by position.
    # This should be a type error as `problematic_callback` expects 0 args
    # but `add_done_callback` provides 1 arg.
    # Some checkers might get this wrong due to the complexity of partial and ParamSpec.
    problematic_callback = partial(reporter.report_error, error_detail="Partial error detail")
    reveal_type(problematic_callback) # Expected: Callable[[asyncio.Task[Any]], None] (if correctly inferred)
    task3.add_done_callback(problematic_callback)


    await asyncio.gather(task1, task2, task3, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_main_call_asyncio_run_main___():
    """Execute main block call: asyncio.run(main())"""
    import traceback as _tb, sys as _sys
    try:
        asyncio.run(main())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 48
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
