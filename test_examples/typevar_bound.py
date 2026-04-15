from typing import Literal, Any, Generic
from typing_extensions import TypeVar


OptionalStructBase = dict[str, Any] | None
OptionalStruct = TypeVar('OptionalStruct', default=None, bound=OptionalStructBase)
Type = TypeVar('Type', bound=Any, default=None)


class DataHandlerBase():
    def apply(struct: OptionalStruct = None) -> Any:
        ...
    
    def struct(**struct: OptionalStructBase) -> Any:
        ...

class DataConcrete(DataHandlerBase, Generic[OptionalStruct, Type]):
    def struct(**struct: OptionalStruct) -> None:
        ...
