from typing import NewType, Tuple, Union, TYPE_CHECKING

UserId = NewType('UserId', int)
ItemId = NewType('ItemId', str)

def process_mixed_data(initial_data: Union[Tuple[UserId, ItemId], Tuple[None, None]]):
    x: UserId | None = None
    y: ItemId | None = None
    data_source: Union[Tuple[UserId, ItemId], Tuple[None, None]] = initial_data

    # The issue here is how `x` and `y` are inferred across loop iterations
    # when reassigned from a potentially changing source `data_source`.
    # `ty` previously marked `x` as Divergent.
    while True:
        x, y = data_source
        if TYPE_CHECKING:
            reveal_type(x) # Expect UserId | None. Some checkers might struggle with the Union.
            reveal_type(y) # Expect ItemId | None.
        
        # Simulate data changing or loop termination
        if x is None:
            break
        data_source = (None, None) # Next iteration will set x, y to None
    
    if TYPE_CHECKING:
        reveal_type(x) # Should be None at loop exit
        reveal_type(y) # Should be None at loop exit


if __name__ == "__main__":
    process_mixed_data((UserId(101), ItemId("item_A")))
    process_mixed_data((None, None))