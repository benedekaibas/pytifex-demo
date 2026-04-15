from __future__ import annotations
from typing import TypeVar, ParamSpec, Callable, NewType, Generic, Self, cast
from dataclasses import dataclass, field

TraceId = NewType("TraceId", str)
# SpecificTraceId values are assignable to TraceId, but TraceId values are NOT assignable to SpecificTraceId.
SpecificTraceId = NewType("SpecificTraceId", TraceId)

P = ParamSpec("P")
R = TypeVar("R")

T = TypeVar("T", bound=TraceId)

def trace_log(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper

@dataclass
class TracedComponent(Generic[T]):
    # This default_factory attempts `cast(T, TraceId("default"))`.
    # When T is TraceId, this is `cast(TraceId, TraceId("default"))`, which is valid.
    # When T is SpecificTraceId, this becomes `cast(SpecificTraceId, TraceId("default"))`.
    # This is a narrowing cast (from supertype TraceId to subtype SpecificTraceId).
    # Some checkers might accept this 'cast' as a directive and ignore the potential runtime error.
    # Other checkers might flag this cast as unsafe or provably incorrect, especially given NewType's nominal behavior.
    trace_id: T = field(default_factory=lambda: cast(T, TraceId("default")))

    @trace_log
    def process_data(self, data: str, count: int) -> tuple[list[str], T]:
        print(f"Processing '{data}' {count} times with trace_id: {self.trace_id}")

        if data == "divergence_case":
            # This return statement is the intended primary divergence point.
            # When T is SpecificTraceId, this becomes `cast(SpecificTraceId, TraceId("divergence_id"))`.
            # If the default_factory cast was accepted, this is another instance of the same narrowing cast.
            # Some checkers might remain lenient on `cast`, others might become stricter.
            return [data], cast(T, TraceId("divergence_id"))

        return ([f"{data}-{i}" for i in range(count)], self.trace_id)

    def get_self_id(self) -> Self:
        return self

if __name__ == "__main__":
    # Removed all `reveal_type` calls to eliminate basic errors/warnings
    # that could mask the intended divergence or cause checkers to fail on unrelated issues.

    # Case 1: T is TraceId. No type errors expected here, as all casts are valid.
    my_component_trace = TracedComponent[TraceId]()
    results_trace, id_trace = my_component_trace.process_data("item_trace", 3)
    print(f"Results Trace: {results_trace}, ID: {id_trace}")
    results_divergence_trace, id_divergence_trace = my_component_trace.process_data("divergence_case", 1)
    print(f"Results Divergence Trace: {results_divergence_trace}, ID: {id_divergence_trace}")

    # Case 2: T is SpecificTraceId.
    # This instantiation will trigger the `default_factory` where T is `SpecificTraceId`.
    # This means `trace_id` attempts `cast(SpecificTraceId, TraceId("default"))`.
    # The `process_data` method's divergence branch will attempt `cast(SpecificTraceId, TraceId("divergence_id"))`.
    # This setup tests how different checkers handle these narrowing casts from a NewType's base to its specific type.
    # Some checkers (like mypy initially) are very lenient with `cast` and might pass.
    # Others might flag these casts as unsafe due to the nominal subtyping of NewTypes.
    # Zuban previously failed on a 'TypeVar is unbound' error for this structure, which would be a divergence itself.
    my_component_specific = TracedComponent[SpecificTraceId]()

    results_divergence_specific, id_divergence_specific = my_component_specific.process_data("divergence_case", 1)
    print(f"Results Divergence Specific: {results_divergence_specific}, ID: {id_divergence_specific}")

    # Further tests to ensure Self and other functionality remains correct
    cloned_component_trace = my_component_trace.get_self_id()
    cloned_component_specific = my_component_specific.get_self_id()

    # This should still be a type error (argument types mismatch) if checkers reach it
    # my_component_trace.process_data(123, "abc")