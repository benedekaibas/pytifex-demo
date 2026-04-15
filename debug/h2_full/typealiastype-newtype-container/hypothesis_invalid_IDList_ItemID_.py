"""Hypothesis-based property test for type constraint validation.

Type annotation: IDList[ItemID]
Test type: invalid
"""\n\n"""Hypothesis test for IDList[ItemID] - invalid values.

Type annotation: IDList[ItemID]
Variable: my_item_ids
Test type: invalid
"""

# Original source code
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

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, IDList[ItemID])
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "IDList[ItemID]" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "IDList[ItemID]" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
