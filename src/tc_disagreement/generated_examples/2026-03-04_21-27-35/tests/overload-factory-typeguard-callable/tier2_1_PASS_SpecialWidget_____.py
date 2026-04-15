"""
Hypothesis Tier 2 — Generated Property Test

Target: SpecialWidget(...)
Kind: constructor
Line: 9
Status: PASS
Max examples: 30

Strategies:
  name: str -> text(max_size=30)
  code: int -> integers(min_value=-1000, max_value=1000)
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(name=..., code=...)
def test_SpecialWidget_constructor(name, code):
    """Property test: SpecialWidget() with generated inputs."""
    instance = SpecialWidget(name, code)
    assert isinstance(instance, SpecialWidget)


if __name__ == "__main__":
    test_SpecialWidget_constructor()
