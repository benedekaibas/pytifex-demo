"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: overload-factory-typeguard-callable.py
Patterns detected: 1
    - decorator_signature (5 tests)
Test cases generated: 5
"""

# --- Original source ---

from typing import overload, Any, Callable, TypeVar, Union
from typing_extensions import TypeGuard, reveal_type

class Widget:
    def __init__(self, name: str) -> None:
        self.name = name

class SpecialWidget(Widget):
    def __init__(self, name: str, code: int) -> None:
        super().__init__(name)
        self.code = code

T = TypeVar("T")

class WidgetFactory:
    @overload
    @classmethod
    def create(cls, name: str) -> Widget: ...
    @overload
    @classmethod
    def create(cls, name: str, code: int) -> SpecialWidget: ...
    @overload
    @classmethod
    def create(cls, filter_prefix: str, *, is_special_widget: bool) -> Callable[[Any], TypeGuard[SpecialWidget]]: ...
    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Union[Widget, SpecialWidget, Callable[[Any], TypeGuard[SpecialWidget]]]:
        if len(args) == 1 and isinstance(args[0], str):
            if "is_special_widget" in kwargs:
                # Third overload: return a TypeGuard callable
                prefix = args[0]
                def is_special_prefixed_widget(obj: Any) -> TypeGuard[SpecialWidget]:
                    return isinstance(obj, SpecialWidget) and obj.name.startswith(prefix)
                return is_special_prefixed_widget
            else:
                # First overload: Widget
                return Widget(args[0])
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            # Second overload: SpecialWidget
            return SpecialWidget(args[0], args[1])
        raise ValueError("Invalid arguments for create method")

def process_widgets(widgets: list[Widget]) -> None:
    # Use the TypeGuard callable created by the factory
    is_special_abc = WidgetFactory.create("abc", is_special_widget=True)
    reveal_type(is_special_abc) # Expected: Callable[[Any], TypeGuard[SpecialWidget]]

    special_widgets_list: list[SpecialWidget] = []
    for w in widgets:
        if is_special_abc(w):
            reveal_type(w) # Expected: SpecialWidget (narrowed)
            special_widgets_list.append(w)
            print(f"Found special widget: {w.name} with code {w.code}")
    reveal_type(special_widgets_list) # Expected: list[SpecialWidget]


if __name__ == "__main__":
    # Test first overload
    widget1 = WidgetFactory.create("Basic")
    reveal_type(widget1) # Expected: Widget

    # Test second overload
    special_widget1 = WidgetFactory.create("Advanced", 123)
    reveal_type(special_widget1) # Expected: SpecialWidget

    # Test third overload
    is_my_special = WidgetFactory.create("my_", is_special_widget=True)
    reveal_type(is_my_special) # Expected: Callable[[Any], TypeGuard[SpecialWidget]]

    widgets_to_process: list[Widget] = [
        WidgetFactory.create("my_alpha"),
        WidgetFactory.create("gamma"),
        WidgetFactory.create("my_beta", 456),
        WidgetFactory.create("another_my_widget", 789),
    ]

    process_widgets(widgets_to_process)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_WidgetFactory_create_decorated_callable():
    """Verify decorated method WidgetFactory.create is callable."""
    try:
        obj = WidgetFactory()
        method = getattr(obj, "create", None)
        if method is None:
            BUGS.append({"line": 18, "type": "AttributeError", "error": "WidgetFactory has no method create after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 18, "type": "TypeError", "error": "WidgetFactory.create is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_WidgetFactory_create_decorated_callable():
    """Verify decorated method WidgetFactory.create is callable."""
    try:
        obj = WidgetFactory()
        method = getattr(obj, "create", None)
        if method is None:
            BUGS.append({"line": 21, "type": "AttributeError", "error": "WidgetFactory has no method create after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 21, "type": "TypeError", "error": "WidgetFactory.create is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 21, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_WidgetFactory_create_decorated_callable():
    """Verify decorated method WidgetFactory.create is callable."""
    try:
        obj = WidgetFactory()
        method = getattr(obj, "create", None)
        if method is None:
            BUGS.append({"line": 24, "type": "AttributeError", "error": "WidgetFactory has no method create after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 24, "type": "TypeError", "error": "WidgetFactory.create is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_WidgetFactory_create_decorated_callable():
    """Verify decorated method WidgetFactory.create is callable."""
    try:
        obj = WidgetFactory()
        method = getattr(obj, "create", None)
        if method is None:
            BUGS.append({"line": 26, "type": "AttributeError", "error": "WidgetFactory has no method create after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 26, "type": "TypeError", "error": "WidgetFactory.create is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 26, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_WidgetFactory_create_no_args():
    """Call decorated WidgetFactory.create with no extra args."""
    try:
        obj = WidgetFactory()
        result = obj.create()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 26, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


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
