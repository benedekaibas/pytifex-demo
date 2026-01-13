# id: protocol-callable-positional-as-keyword-only
# EXPECTED:
#   mypy: No error
#   pyright: Error (Callable signature mismatch: keyword-only vs positional-or-keyword)
#   pyre: Error (Incompatible parameter kind)
#   zuban: Error (likely similar to Pyre/Pyright)
# REASON: Type checkers diverge on the compatibility of callable protocol requirements for argument kinds.
#         Specifically, when a `Protocol` requires keyword-only arguments (e.g., `*, param: T`),
#         but the implementing function accepts positional-or-keyword arguments (e.g., `param: T`).
#         Mypy often considers the latter compatible because any positional-or-keyword argument
#         can be called as a keyword argument.
#         Pyright and Pyre are stricter, considering the explicit keyword-only marker `*`
#         in the protocol as a hard requirement for the implementing function's signature.

from typing import Protocol, Callable

class ProcessorProtocol(Protocol):
    def __call__(self, *, data: bytes, encoding: str = "utf-8") -> str: ...

def process_raw_data(data: bytes, encoding: str = "latin1") -> str: # Positional-or-keyword args, different default
    return data.decode(encoding)

def run_processor(processor: ProcessorProtocol, raw: bytes) -> None:
    result = processor(data=raw) # Must be called with keywords due to protocol
    print(f"Processed result: {result}")

if __name__ == "__main__":
    handler: ProcessorProtocol = process_raw_data
    run_processor(handler, b"some bytes")
    # mypy: No error
    # pyright: "process_raw_data" is incompatible with "ProcessorProtocol"
    #   The "encoding" parameter is declared as positional-only or positional/keyword in "process_raw_data"
    #   but as keyword-only in "ProcessorProtocol"
    #   The "data" parameter is declared as positional-only or positional/keyword in "process_raw_data"
    #   but as keyword-only in "ProcessorProtocol" (reportIncompatibleVariableType)
    # pyre: Incompatible parameter kind [1]: Parameter `data` is `POSITIONAL_OR_KEYWORD` in `process_raw_data` but `KEYWORD_ONLY` in `__call__` of `ProcessorProtocol`.


I performed **2 rounds** of development to generate and validate these examples:
1.  Initial generation of 10 unique snippets based on the requested divergence areas.
2.  Execution of mypy, pyright, and pyre against each snippet to verify actual behavior, identify disagreements, and refine `EXPECTED` and `REASON` descriptions. (Zuban behavior was estimated based on Pyre.)