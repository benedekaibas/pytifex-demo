from typing import TypeIs, reveal_type, Any, Callable

class StringCheckDescriptor:
    def __get__(self, instance: Any, owner: Any) -> Callable[[Any], TypeIs[str]]:
        def _is_string(val: object) -> TypeIs[str]:
            return isinstance(val, str)
        return _is_string

class MyClassWithDescriptor:
    is_string_via_descriptor = StringCheckDescriptor()

def process_val_with_descriptor(val: object):
    if MyClassWithDescriptor().is_string_via_descriptor(val):
        reveal_type(val) # Expected: str
    else:
        reveal_type(val) # Expected: object (or object - str)
        
if __name__ == "__main__":
    process_val_with_descriptor("hello world")
    process_val_with_descriptor(12345)
    process_val_with_descriptor(True)