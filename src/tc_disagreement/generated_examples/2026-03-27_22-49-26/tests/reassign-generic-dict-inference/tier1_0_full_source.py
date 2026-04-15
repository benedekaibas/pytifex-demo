from typing import TypeVar, Dict, Any, TYPE_CHECKING, NewType, Union

T = TypeVar('T')
UserId = NewType('UserId', int)
ProductId = NewType('ProductId', str)

def create_metadata(key_id: T, description: str) -> Dict[str, Union[T, str]]:
    """Creates a dictionary with generic ID and string description."""
    return {"id": key_id, "desc": description, "type_name": str(type(key_id).__name__)}

if __name__ == "__main__":
    # Initial assignment with int as T
    data_record = create_metadata(1, "system log entry")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, int | str]
        reveal_type(data_record["id"]) # Expected int | str
    assert data_record["id"] == 1
    print(f"Record 1: {data_record}")

    # Reassignment with NewType(UserId) as T.
    # Type checkers must correctly update the type of `data_record` and its elements.
    data_record = create_metadata(UserId(101), "user activity")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, UserId | str] (not int | str)
        reveal_type(data_record["id"]) # Expected UserId | str (not int | str)
    assert data_record["id"] == UserId(101)
    print(f"Record 2: {data_record}")

    # Reassignment with another NewType(ProductId) as T.
    data_record = create_metadata(ProductId("PROD-XYZ"), "product info")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, ProductId | str]
        reveal_type(data_record["id"]) # Expected ProductId | str
    assert data_record["id"] == ProductId("PROD-XYZ")
    print(f"Record 3: {data_record}")

    # Reassignment to a different generic type (e.g., bool)
    data_record = create_metadata(True, "boolean flag")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, bool | str]
        reveal_type(data_record["id"]) # Expected bool | str
    assert data_record["id"] is True
    print(f"Record 4: {data_record}")