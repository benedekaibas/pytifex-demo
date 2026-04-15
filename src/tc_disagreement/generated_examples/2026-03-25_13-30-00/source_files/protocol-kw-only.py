from typing import Protocol, Callable


class Callback(Protocol):
    def __call__(self, x: int, *, kw_only: str = "default") -> None: ...


def invoke(cb: Callback, arg: int) -> None:
    cb(arg)


def my_callback(x: int, kw_only: str = "modified") -> None:
    pass


invoke(my_callback, 42)

if __name__ == "__main__":
    pass
