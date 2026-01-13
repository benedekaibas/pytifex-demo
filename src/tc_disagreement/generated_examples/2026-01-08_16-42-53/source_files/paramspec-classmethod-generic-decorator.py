# id: paramspec-classmethod-generic-decorator
# EXPECTED:
#   mypy: Error (signature mismatch in decorator application)
#   pyright: No error
#   pyre: No error
#   zuban: Error (likely similar to Mypy)
# REASON: Mypy can be stricter when applying `ParamSpec`-based decorators to `classmethod`s,
#         especially regarding the `cls` parameter. It might fail to correctly infer or preserve
#         the signature, leading to an error about the type of `classmethod` not matching the
#         `Callable` expected by `ParamSpec`. Pyright and Pyre often have more robust handling
#         of `ParamSpec` with `classmethod`s and `staticmethod`s,
#         correctly adapting the signature.

from typing import TypeVar, Callable, Type, Any
from typing_extensions import ParamSpec

P = ParamSpec('P')
R = TypeVar('R')

def debug_log(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class Logger:
    @debug_log
    @classmethod
    def create_instance(cls: Type["Logger"], name: str, config: dict[Any, Any]) -> "Logger":
        print(f"Creating Logger instance '{name}' with config {config}")
        return cls()

    @debug_log
    def log_message(self, message: str) -> None:
        print(f"Instance log: {message}")

if __name__ == "__main__":
    Logger.create_instance("main_logger", {"level": "INFO"})
    # mypy: Argument 1 to "debug_log" has incompatible type "classmethod[Callable[[Type[Logger], str, dict[Any, Any]], Logger]]"; expected "Callable[[_P], _R]" [arg-type]
    # pyright: No error
    # pyre: No error