# id: self-in-generic-container-return
# EXPECTED:
#   mypy: Error (incompatible return type, Self not correctly inferred in tuple)
#   pyright: No error
#   pyre: Error (incompatible return type)
#   zuban: Error (likely similar to Mypy/Pyre)
# REASON: Type checkers diverge on the robustness of `Self` resolution when it's nested
#         within another generic type in a return annotation, particularly in a method
#         of a generic class. Mypy and Pyre may struggle to correctly infer that `tuple[Self, ...]`
#         should resolve to `tuple[ConcreteType, ...]` when `Self` refers to the concrete
#         instantiation of the generic class, leading to errors in the implementing method's
#         return type or during usage. Pyright is typically more sophisticated in resolving
#         `Self` across such nested generic contexts.

from typing import Generic, TypeVar, Tuple
from typing_extensions import Self
from abc import ABC, abstractmethod

ItemType = TypeVar('ItemType')

class ItemProcessor(ABC, Generic[ItemType]):
    @abstractmethod
    def process_item(self, item: ItemType) -> ItemType: ...

    @classmethod
    @abstractmethod
    def create_batch_processor(cls) -> Tuple[Self, ...]:
        """Method returns a tuple of Self instances."""
        ...

class StringProcessor(ItemProcessor[str]):
    def process_item(self, item: str) -> str:
        return item.upper()

    @classmethod
    def create_batch_processor(cls) -> Tuple[Self, ...]:
        # Here, Self should be StringProcessor.
        # So it returns Tuple[StringProcessor, ...]
        return (cls(), cls())

if __name__ == "__main__":
    batch = StringProcessor.create_batch_processor()
    # mypy: Incompatible return value type (got "tuple[StringProcessor, StringProcessor]", expected "tuple[Self, ...]") [return-value]
    # pyright: No error
    # pyre: Incompatible return type [7]: Expected `Tuple[typing_extensions.Self, ...]` but got `Tuple[StringProcessor, StringProcessor]`.