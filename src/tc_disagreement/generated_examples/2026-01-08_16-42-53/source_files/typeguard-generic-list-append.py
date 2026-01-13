# id: typeguard-generic-list-append
# EXPECTED:
#   mypy: Error (list not narrowed, append expects original generic base)
#   pyright: No error
#   pyre: No error
#   zuban: No error (likely similar to Pyright/Pyre)
# REASON: Mypy can be conservative when narrowing generic container types with `TypeGuard`.
#         Even if the `TypeGuard` is designed to narrow `list[object]` to `list[T]`,
#         mypy may not fully apply this narrowing for operations like `append`,
#         insisting on the original base type of the list elements (e.g., `Union[int, str]`).
#         Pyright and Pyre are generally more advanced in their generic narrowing capabilities,
#         allowing such operations on the narrowed list.

from typing import TypeGuard, TypeVar, List, Union

T = TypeVar('T')

def is_list_of(val: list[Union[int, str]], item_type: type[T]) -> TypeGuard[list[T]]:
    """Checks if a list contains only items of a specific type."""
    return all(isinstance(x, item_type) for x in val)

def process_data(data: List[Union[int, str]]) -> None:
    if is_list_of(data, str):
        # 'data' should be narrowed to 'list[str]' here.
        data.append("new_string") # Mypy often errors here, expecting `Union[int, str]`

if __name__ == "__main__":
    my_data: List[Union[int, str]] = ["initial", 123]
    process_data(["foo", "bar"])
    # mypy: Argument 1 to "append" of "list" has incompatible type "Literal['new_string']"; expected "Union[int, str]" [arg-type]
    # pyright: No error
    # pyre: No error