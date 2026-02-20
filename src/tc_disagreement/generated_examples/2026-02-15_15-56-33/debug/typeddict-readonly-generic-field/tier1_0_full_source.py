from typing import List, TypeVar, Any
from typing_extensions import TypedDict, ReadOnly

# Inspired by pyright#11037 - ReadOnly fields and TypedDict inheritance.
# This adds generics to the ReadOnly field to test for deeper interaction issues.

T = TypeVar("T")

class ItemMeta(TypedDict):
    id: str
    tags: ReadOnly[List[str]] # A ReadOnly list of strings

class GenericContainer[T](TypedDict):
    name: str
    items: ReadOnly[List[T]] # A ReadOnly list of generic type T

class ConcreteContainer(GenericContainer[ItemMeta]):
    # Inherits 'items' as ReadOnly[List[ItemMeta]]
    description: str

def update_container_items(container: ConcreteContainer) -> None:
    """Attempts to mutate the ReadOnly 'items' list and its elements."""
    print(f"Updating container: {container['name']}")
    
    # This should be an error: 'items' itself is ReadOnly.
    # container["items"] = [{"id": "new", "tags": []}] # Expected error

    # This should be an error: Attempting to modify the ReadOnly list via append.
    # ReadOnly[List[T]] implies the list's contents cannot be modified.
    if container["items"]:
        # container["items"].append({"id": "added", "tags": []}) # <--- EXPECTED DIVERGENCE: Should this be an error?

        # This should also be an error: `tags` is `ReadOnly[List[str]]` inside `ItemMeta`.
        # Some checkers might not propagate ReadOnly's immutability deeply.
        if container["items"][0] and "tags" in container["items"][0]:
            # container["items"][0]["tags"].append("new_tag") # <--- EXPECTED DIVERGENCE: Should this be an error?
            pass # Commented out for code execution.

    # Modifying a field *within* an element of the ReadOnly list, where that field is mutable.
    # This should be allowed because `ItemMeta` itself is mutable (only its `tags` field is `ReadOnly`).
    if container["items"]:
        container["items"][0]["id"] = "modified_id" # No error expected
        
if __name__ == "__main__":
    my_item: ItemMeta = {"id": "item1", "tags": ["tagA", "tagB"]}
    my_container: ConcreteContainer = {
        "name": "My Box",
        "items": [my_item, {"id": "item2", "tags": []}],
        "description": "A box of items"
    }
    update_container_items(my_container)
    print(f"Container after updates: {my_container}")