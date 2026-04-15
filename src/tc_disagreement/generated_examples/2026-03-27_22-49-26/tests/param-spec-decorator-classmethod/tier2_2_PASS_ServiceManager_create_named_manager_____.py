"""
Hypothesis Tier 2 — Generated Property Test

Target: ServiceManager.create_named_manager(...)
Kind: function
Line: 24
Status: PASS
Max examples: 30

Strategies:
  base_name: str -> text(max_size=30)
  suffix: str -> text(max_size=30)
"""

# --- Original source (full context) ---

from typing import Callable, ParamSpec, TypeVar, Any, TYPE_CHECKING, ClassVar
import functools

P = ParamSpec('P')
R = TypeVar('R')

def record_call(func: Callable[P, R]) -> Callable[P, R]:
    """A decorator that records calls."""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"RECORDING CALL: {func.__qualname__} with {args}, {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class ServiceManager:
    _instance_count: ClassVar[int] = 0

    def __init__(self, name: str):
        self.name = name
        ServiceManager._instance_count += 1
    
    @classmethod
    @record_call
    def create_named_manager(cls, base_name: str, suffix: str) -> "ServiceManager":
        """Creates a ServiceManager instance with a combined name."""
        return cls(f"{base_name}-{suffix}")

    @record_call
    def shutdown(self, reason: str = "normal") -> str:
        """Shuts down the manager."""
        return f"{self.name} shutting down due to {reason}"

    @staticmethod
    @record_call
    def get_total_managers() -> int:
        """Returns the total number of manager instances."""
        return ServiceManager._instance_count

if __name__ == "__main__":
    # Test 1: Classmethod via class
    manager_alpha = ServiceManager.create_named_manager("Alpha", "Prod")
    if TYPE_CHECKING:
        # Checkers may struggle to correctly infer the return type of a decorated classmethod,
        # especially when ParamSpec is involved, or track it after reassignment.
        reveal_type(manager_alpha) # Expected ServiceManager
        reveal_type(ServiceManager.create_named_manager) # Expected Callable[[Type[ServiceManager], str, str], ServiceManager]
    assert manager_alpha.name == "Alpha-Prod"
    print(f"Created manager: {manager_alpha.name}")

    # Test 2: Classmethod via instance (should still work and be typed correctly)
    manager_beta = manager_alpha.create_named_manager("Beta", "Dev")
    if TYPE_CHECKING:
        reveal_type(manager_beta) # Expected ServiceManager
    assert manager_beta.name == "Beta-Dev"
    print(f"Created manager: {manager_beta.name}")

    # Test 3: Instance method
    shutdown_msg = manager_alpha.shutdown("emergency")
    if TYPE_CHECKING:
        reveal_type(shutdown_msg) # Expected str
    print(shutdown_msg)

    # Test 4: Static method
    total_managers = ServiceManager.get_total_managers()
    if TYPE_CHECKING:
        reveal_type(total_managers) # Expected int
    print(f"Total managers: {total_managers}")

    # Test 5: Reassignment and re-check for inference reset (zuban issue #115 inspiration)
    # The variable `manager_ref` changes its source from a classmethod call to a staticmethod call (different return type).
    manager_ref: ServiceManager | int
    manager_ref = ServiceManager.create_named_manager("Gamma", "Test")
    if TYPE_CHECKING:
        reveal_type(manager_ref) # Expected ServiceManager
    print(f"Manager ref (ServiceManager): {manager_ref.name}")

    manager_ref = ServiceManager.get_total_managers()
    if TYPE_CHECKING:
        reveal_type(manager_ref) # Expected int (should reset from ServiceManager)
    print(f"Manager ref (int): {manager_ref}")


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(base_name=..., suffix=...)
def test_ServiceManager_create_named_manager(base_name, suffix):
    """Property test: ServiceManager.create_named_manager() with generated inputs."""
    result = ServiceManager.create_named_manager(base_name, suffix)


if __name__ == "__main__":
    test_ServiceManager_create_named_manager()
