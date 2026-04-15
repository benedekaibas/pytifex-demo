"""
Hypothesis Tier 2 — Generated Property Test

Target: TaskReporter.report_done(...)
Kind: method
Line: 17
Status: PASS
Max examples: 30

Strategies:
  task: Task -> from_type(_asyncio.Task[typing.Any])
  extra_msg: str -> text(max_size=30)
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(receiver=..., task=..., extra_msg=...)
def test_TaskReporter_report_done(receiver, task, extra_msg):
    """Property test: TaskReporter.report_done() with generated inputs."""
    result = receiver.report_done(task, extra_msg)
    # Expected return type: NoneType


if __name__ == "__main__":
    test_TaskReporter_report_done()
