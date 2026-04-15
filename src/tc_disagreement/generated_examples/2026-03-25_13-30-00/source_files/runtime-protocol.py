from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...


class Resource:
    def close(self) -> None:
        pass


def cleanup(r: SupportsClose) -> None:
    r.close()


r = Resource()
cleanup(r)

if __name__ == "__main__":
    pass
