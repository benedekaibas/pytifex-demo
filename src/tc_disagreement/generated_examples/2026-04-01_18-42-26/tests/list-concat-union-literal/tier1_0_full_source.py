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