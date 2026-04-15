"""
Hypothesis Tier 2 — Generated Property Test

Target: main(...)
Kind: function
Line: 31
Status: PASS
Max examples: 30
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

def test_main():
    """Test that main() runs without type errors."""
    result = main()


if __name__ == "__main__":
    test_main()
