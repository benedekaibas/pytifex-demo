"""
Hypothesis Tier 2 — Generated Property Test

Target: process_events(...)
Kind: function
Line: 3
Status: PASS
Max examples: 30

Strategies:
  events: list -> lists(one_of(just('start'), just('stop')), max_size=5)
"""

# --- Original source (full context) ---

from typing import Literal, Union, reveal_type

def process_events(events: list[Union[Literal["start"], Literal["stop"]]]) -> None:
    for event in events:
        print(f"Event: {event}")

if __name__ == "__main__":
    starts: list[Literal["start"]] = ["start", "start"]
    stops: list[Literal["stop"]] = ["stop"]

    # Concatenating lists of different Literals which should resolve to a Union type.
    # Some checkers might be very strict on the exact Literal type during concatenation.
    all_events: list[Union[Literal["start"], Literal["stop"]]] = starts + stops
    reveal_type(all_events)

    process_events(all_events)


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(events=...)
def test_process_events(events):
    """Property test: process_events() with generated inputs."""
    result = process_events(events)


if __name__ == "__main__":
    test_process_events()
