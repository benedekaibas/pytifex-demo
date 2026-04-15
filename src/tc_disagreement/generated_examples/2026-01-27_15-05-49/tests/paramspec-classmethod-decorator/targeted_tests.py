"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: paramspec-classmethod-decorator.py
Patterns detected: 1
    - callable_param (3 tests)
Test cases generated: 3
"""

# --- Original source ---

from typing import TypeVar, ParamSpec, Callable, Type, ClassVar, reveal_type, Concatenate
from functools import wraps

R = TypeVar("R")
P = ParamSpec("P")
T_Cls = TypeVar("T_Cls", bound="BaseProcessor")

def class_method_logger(f: Callable[Concatenate[Type[T_Cls], P], R]) -> Callable[Concatenate[Type[T_Cls], P], R]:
    """
    A decorator for class methods that uses ParamSpec to preserve the method signature,
    including the `cls` argument.
    """
    @wraps(f)
    def wrapper(cls: Type[T_Cls], *args: P.args, **kwargs: P.kwargs) -> R:
        print(f"[{cls.__name__}] Calling class method '{f.__name__}' with args: {args}, kwargs: {kwargs}")
        return f(cls, *args, **kwargs)
    return wrapper

class BaseProcessor:
    _instance_count: ClassVar[int] = 0

    def __init__(self, name: str):
        self.name = name
        BaseProcessor._instance_count += 1
    
    @classmethod
    @class_method_logger
    def create_named_instance(cls: Type[T_Cls], prefix: str, id_num: int) -> T_Cls:
        """
        A class method that creates an instance, decorated with a ParamSpec-aware decorator.
        `P` should capture `(prefix: str, id_num: int)`.
        `T_Cls` should be the specific class (e.g., `MySpecialProcessor`).
        """
        instance_name = f"{prefix}-{id_num}"
        return cls(instance_name)

    @classmethod
    def get_total_instances(cls) -> int:
        return cls._instance_count

class MySpecialProcessor(BaseProcessor):
    def __init__(self, name: str):
        super().__init__(name)
        self.special_id = name.split('-')[-1] # Extract ID from name

    def get_special_id(self) -> str:
        return self.special_id

if __name__ == "__main__":
    # Call the decorated class method on the base class
    proc1 = BaseProcessor.create_named_instance("Base", 1)
    reveal_type(proc1) # Expected: BaseProcessor

    # Call the decorated class method on the derived class
    proc2 = MySpecialProcessor.create_named_instance("Special", 2)
    reveal_type(proc2) # Expected: MySpecialProcessor

    print(f"Processor 1 name: {proc1.name}")
    print(f"Processor 2 name: {proc2.name}, Special ID: {proc2.get_special_id()}") # Should be valid

    total_instances = BaseProcessor.get_total_instances()
    print(f"Total instances created: {total_instances}") # Expected: 2

    print("\nExample demonstrating ParamSpec with `Concatenate` in a decorator for class methods.")
    print("Checks if the decorator correctly preserves the `cls` argument and the remaining `ParamSpec` arguments.")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_class_method_logger_none_callable():
    """Call class_method_logger with None for Callable param 'f'."""
    try:
        class_method_logger(f=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_class_method_logger_string_callable():
    """Call class_method_logger with a string for Callable param 'f'."""
    try:
        class_method_logger(f="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_class_method_logger_wrong_arity_callable():
    """Call class_method_logger with a zero-arg callable for param 'f'."""
    try:
        class_method_logger(f=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 8, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
