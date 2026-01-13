# id: typevar-double-bound-with-generic-instantiation
# EXPECTED:
#   mypy: Error (TypeVar bound incompatible with generic instantiation)
#   pyright: No error
#   pyre: Error (TypeVar bound incompatible)
#   zuban: Error (likely similar to Mypy/Pyre)
# REASON: Type checkers differ on the complexity and depth of `TypeVar` bound checking,
#         especially when a `TypeVar` is bound to a generic class *and* that generic class
#         itself takes another `TypeVar` as a parameter.
#         Mypy and Pyre can struggle to reconcile the bound `Logger[str]` with a function
#         that accepts `Logger[T]` where `T` is a different `TypeVar`, leading to
#         incompatibility errors even if the structure appears logically sound.
#         Pyright is often more flexible in resolving these complex generic bounds,
#         correctly identifying that `Logger[str]` can satisfy a bound of `Logger[object]`
#         if `Logger` is covariant in its type parameter.

from typing import TypeVar, Generic, List

T = TypeVar('T')

class Logger(Generic[T]):
    def __init__(self, items: List[T]) -> None:
        self.items = items

    def log_items(self) -> None:
        for item in self.items:
            print(f"Logging: {item}")

U = TypeVar('U', bound=Logger[object]) # U must be a Logger whose items are at least `object`

def process_generic_logger(logger: U) -> None:
    logger.log_items()

if __name__ == "__main__":
    string_logger = Logger(["hello", "world"])
    process_generic_logger(string_logger)
    # mypy: Argument 1 to "process_generic_logger" has incompatible type "Logger[str]"; expected "U" [arg-type]
    # mypy: TypeVar "U" defined with "bound=Logger[object]"
    # pyright: No error
    # pyre: Expected `U` for 1st argument but got `Logger[str]`.