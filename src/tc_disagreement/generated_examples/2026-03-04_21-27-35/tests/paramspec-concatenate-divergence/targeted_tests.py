"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: paramspec-concatenate-divergence.py
Patterns detected: 2
    - callable_param (3 tests)
  - main_block_replay (1 tests)
Test cases generated: 4
"""

# --- Original source ---

import asyncio
from typing import ParamSpec, Callable, Any, TypeVar, Concatenate
from typing_extensions import reveal_type

P = ParamSpec("P")
R = TypeVar("R")

async def calculate_sum(a: int, b: int) -> int:
    await asyncio.sleep(0.01)
    return a + b

class ResultHandler:
    def __init__(self, tag: str) -> None:
        self.tag = tag

    def handle_result(self, task: asyncio.Task[Any], **kwargs: Any) -> None:
        status = kwargs.get("status", "completed")
        print(f"[{self.tag}] Task '{task.get_name()}' {status}. Result: {task.result()}")
        if kwargs:
            print(f"  Extra kwargs: {kwargs}")

    def handle_specific(self, task: asyncio.Task[int]) -> None:
        print(f"[{self.tag}] Specific handler for int task: {task.result()}")

# This wrapper aims to bind specific arguments to a handler that expects
# an asyncio.Task[Any] as its first positional argument, followed by
# other arguments which are captured by ParamSpec P.
def generic_callback_wrapper(
    handler: Callable[Concatenate[asyncio.Task[Any], P], R],
    *args_to_bind: P.args,
    **kwargs_to_bind: P.kwargs
) -> Callable[[asyncio.Task[Any]], None]:
    """
    Creates a wrapper function suitable for asyncio.Task.add_done_callback.
    The `handler` must accept `asyncio.Task[Any]` as its first positional argument.
    The `*args_to_bind` and `**kwargs_to_bind` must match the remaining arguments of `handler` (P).
    """
    def wrapper_func(task: asyncio.Task[Any]) -> None:
        try:
            # The type checker should now correctly validate that this call
            # matches the handler's signature defined with Concatenate and P.
            handler(task, *args_to_bind, **kwargs_to_bind)
        except TypeError:
            # This fallback is for runtime behavior, not type checking.
            print(f"[{handler.__name__}] Failed to call handler with provided args/kwargs for task {task.get_name()}")
    return wrapper_func

async def main():
    handler = ResultHandler("MAIN")

    task1 = asyncio.create_task(calculate_sum(1, 2), name="sum_task_1")
    # EXPECTED DIVERGENCE/ERROR: handler.handle_result takes **kwargs: Any,
    # which makes it incompatible with Callable[[Task[Any]], None] required by add_done_callback.
    # Some type checkers might be stricter than others here with `**kwargs: Any` compatibility.
    task1.add_done_callback(handler.handle_result)

    task2 = asyncio.create_task(calculate_sum(3, 4), name="sum_task_2")
    # This should be fine due to covariance Task[int] -> Task[Any] and exact signature match.
    task2.add_done_callback(handler.handle_specific)

    task3 = asyncio.create_task(calculate_sum(5, 6), name="sum_task_3")
    # handler.handle_result expects (task, **kwargs). P becomes (**kwargs).
    # 'status="finished"' matches **kwargs. This should pass.
    wrapped_callback = generic_callback_wrapper(handler.handle_result, status="finished")
    reveal_type(wrapped_callback) # Expected: Callable[[asyncio.Task[Any]], None]
    task3.add_done_callback(wrapped_callback)

    task4 = asyncio.create_task(calculate_sum(7, 8), name="sum_task_4")
    # EXPECTED DIVERGENCE/ERROR: handler.handle_specific expects (task: Task[int]),
    # so its remaining parameters 'P' are empty.
    # Passing `extra="info"` to `kwargs_to_bind` should be a type error because
    # an empty P.kwargs cannot accept any keyword arguments.
    # The handling of an empty ParamSpec's `kwargs` by different type checkers
    # is a common source of divergence.
    problematic_wrapped = generic_callback_wrapper(handler.handle_specific, extra="info")
    reveal_type(problematic_wrapped) # Expected: Callable[[asyncio.Task[Any]], None]
    task4.add_done_callback(problematic_wrapped)

    await asyncio.gather(task1, task2, task3, task4, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_generic_callback_wrapper_none_callable():
    """Call generic_callback_wrapper with None for Callable param 'handler'."""
    try:
        generic_callback_wrapper(handler=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 28, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_generic_callback_wrapper_string_callable():
    """Call generic_callback_wrapper with a string for Callable param 'handler'."""
    try:
        generic_callback_wrapper(handler="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 28, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_generic_callback_wrapper_wrong_arity_callable():
    """Call generic_callback_wrapper with a zero-arg callable for param 'handler'."""
    try:
        generic_callback_wrapper(handler=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 28, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


def test_main_call_asyncio_run_main___():
    """Execute main block call: asyncio.run(main())"""
    import traceback as _tb, sys as _sys
    try:
        asyncio.run(main())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 82
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
