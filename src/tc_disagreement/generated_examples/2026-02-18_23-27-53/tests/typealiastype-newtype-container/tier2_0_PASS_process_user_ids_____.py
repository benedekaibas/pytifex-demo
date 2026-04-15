"""
Hypothesis Tier 2 — Generated Property Test

Target: process_user_ids(...)
Kind: function
Line: 11
Status: PASS
Max examples: 30

Strategies:
  ids: IDList -> lists(integers())
"""

# --- Original source (full context) ---

from typing import TypeAliasType, NewType, List, TypeVar, reveal_type

UserID = NewType('UserID', int)
ItemID = NewType('ItemID', str)

T = TypeVar('T')

# TypeAliasType for a generic list of some ID type
IDList = TypeAliasType('IDList', List[T], type_params=(T,))

def process_user_ids(ids: IDList[UserID]):
    reveal_type(ids) # Expected: List[UserID]
    first_id = ids[0]
    reveal_type(first_id) # Expected: UserID
    
    # This assignment is problematic. Some checkers allow List[int] to be assigned to List[NewType(int)],
    # while others might flag it, testing covariance rules for NewType.
    ids_from_raw_ints: IDList[UserID] = [100, 200] # type: ignore # This line is specifically for disagreement.
    reveal_type(ids_from_raw_ints) # Expected: List[UserID]

def test_newtype_typealiastype():
    my_user_ids: IDList[UserID] = IDList([UserID(1), UserID(2)])
    process_user_ids(my_user_ids)

    my_item_ids: IDList[ItemID] = IDList([ItemID("A1"), ItemID("B2")])
    reveal_type(my_item_ids) # Expected: List[ItemID]
    
if __name__ == "__main__":
    test_newtype_typealiastype()


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(ids=...)
def test_process_user_ids(ids):
    """Property test: process_user_ids() with generated inputs."""
    result = process_user_ids(ids)


if __name__ == "__main__":
    test_process_user_ids()
