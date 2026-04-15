from typing import TypeGuard


def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)


def process(items: list[str]) -> None:
    reveal_type(items)


values: list[object] = ["a", "b", "c"]
if is_str_list(values):
    process(values)

if __name__ == "__main__":
    pass
