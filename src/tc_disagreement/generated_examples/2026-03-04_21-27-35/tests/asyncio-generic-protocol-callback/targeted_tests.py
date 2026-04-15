"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: asyncio-generic-protocol-callback.py
Patterns detected: 2
    - protocol_conformance (3 tests)
  - main_block_replay (1 tests)
Test cases generated: 4
"""

# --- Original source ---

import asyncio
from typing import Protocol, TypeVar, Generic, Any, Callable
from typing_extensions import reveal_type

T = TypeVar("T")

class TaskResultProcessor(Protocol[T]):
    def process_result(self, task: asyncio.Task[T], metadata: str = "default") -> None: ...

class MyStringProcessor:
    def process_result(self, task: asyncio.Task[str], metadata: str = "custom") -> None:
        print(f"String Processor: {task.result()} (meta: {metadata})")

class MyIntProcessor:
    def process_result(self, task: asyncio.Task[int], metadata: str = "default") -> None:
        print(f"Int Processor: {task.result()} (meta: {metadata})")

async def some_int_task() -> int:
    await asyncio.sleep(0.01)
    return 42

async def some_str_task() -> str:
    await asyncio.sleep(0.01)
    return "hello"

def wrap_processor_for_callback[T](processor: TaskResultProcessor[T]) -> Callable[[asyncio.Task[T]], None]:
    def callback(task: asyncio.Task[T]) -> None:
        processor.process_result(task) # Using default metadata
    return callback

async def main():
    int_processor = MyIntProcessor()
    str_processor = MyStringProcessor()

    task1 = asyncio.create_task(some_int_task(), name="int_task")
    task1.add_done_callback(wrap_processor_for_callback(int_processor))

    task2 = asyncio.create_task(some_str_task(), name="str_task")
    task2.add_done_callback(wrap_processor_for_callback(str_processor))

    # What if we directly pass a method with default args?
    # This should be a type error as `process_result` has an extra default arg.
    # Type checkers might disagree due to `Callable` variance or `ParamSpec` behavior,
    # or general leniency for `add_done_callback`'s argument.
    task3 = asyncio.create_task(some_int_task(), name="int_task_direct")
    reveal_type(int_processor.process_result) # Expected: Callable[[asyncio.Task[int], str], None]
    task3.add_done_callback(int_processor.process_result) # Should be error for mypy, might pass elsewhere.

    await asyncio.gather(task1, task2, task3, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_MyStringProcessor_has_process_result():
    """Verify MyStringProcessor has required protocol method 'process_result'."""
    try:
        obj = MyStringProcessor()
        method = getattr(obj, "process_result", None)
        if method is None:
            BUGS.append({"line": 7, "type": "AttributeError", "error": "MyStringProcessor missing protocol method process_result", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 7, "type": "TypeError", "error": "MyStringProcessor.process_result is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_MyIntProcessor_has_process_result():
    """Verify MyIntProcessor has required protocol method 'process_result'."""
    try:
        obj = MyIntProcessor()
        method = getattr(obj, "process_result", None)
        if method is None:
            BUGS.append({"line": 7, "type": "AttributeError", "error": "MyIntProcessor missing protocol method process_result", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 7, "type": "TypeError", "error": "MyIntProcessor.process_result is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_TaskResultProcessor_non_conforming_object():
    """Pass a non-conforming object where Protocol TaskResultProcessor is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


def test_main_call_asyncio_run_main___():
    """Execute main block call: asyncio.run(main())"""
    import traceback as _tb, sys as _sys
    try:
        asyncio.run(main())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 52
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
