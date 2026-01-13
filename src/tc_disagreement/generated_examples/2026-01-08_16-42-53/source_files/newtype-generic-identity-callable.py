# id: newtype-generic-identity-callable
# EXPECTED:
#   mypy: No error (treats NewType and base as compatible for identity check in generic)
#   pyright: Error (incompatible type for TypeVar bound)
#   pyre: Error (incompatible type for TypeVar bound)
#   zuban: Error (likely similar to Pyre/Pyright)
# REASON: Type checkers diverge on how strictly they enforce the nominal distinction of `NewType`
#         when it interacts with generic functions or `TypeVar` bounds, particularly in the context
#         of runtime `isinstance` checks that involve the `NewType` itself.
#         Mypy might sometimes treat a `NewType` as sufficiently "compatible" with its base type
#         for generic type identity comparisons, especially if the underlying runtime type is the same.
#         Pyright and Pyre are often more rigorous, flagging a type mismatch if a `NewType` is
#         passed where a raw base type (or its generic equivalent) is expected, even if their
#         runtime `type` objects are the same.

from typing import NewType, TypeVar, Generic, Type, List

OrderId = NewType('OrderId', int)
T = TypeVar('T')

class Processor(Generic[T]):
    def __init__(self, item_type: Type[T]) -> None:
        self.item_type = item_type

    def process(self, value: T) -> str:
        return f"Processing {self.item_type.__name__}: {value}"

def create_processor(item_class: Type[T]) -> Processor[T]:
    return Processor(item_class)

if __name__ == "__main__":
    int_processor = create_processor(int)
    print(int_processor.process(123))

    order_id_processor = create_processor(OrderId)
    print(order_id_processor.process(OrderId(456)))
    # mypy: No error
    # pyright: Argument of type "Type[OrderId]" cannot be assigned to parameter "item_class" of type "Type[T]" in function "create_processor"
    # pyre: Expected `typing.Type[T]` for 1st argument but got `typing.Type[OrderId]`.
