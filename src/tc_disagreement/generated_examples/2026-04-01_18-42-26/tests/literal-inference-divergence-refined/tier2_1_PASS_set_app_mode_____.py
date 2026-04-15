"""
Hypothesis Tier 2 — Generated Property Test

Target: set_app_mode(...)
Kind: function
Line: 12
Status: PASS
Max examples: 30

Strategies:
  mode: Literal -> sampled_from(['production', 'development', 'staging'])
"""

# --- Original source (full context) ---

from typing import Literal

class AppConfig:
    # DEFAULT_MODE is no longer explicitly typed as 'str'.
    # Its runtime value is 'production'.
    # Type checkers will now need to infer its type.
    DEFAULT_MODE = 'production'

# Define a Literal type for allowed modes.
Mode = Literal['production', 'development', 'staging']

def set_app_mode(mode: Mode) -> None:
    print(f"App mode set to: {mode}")

if __name__ == "__main__":
    # Case 1: Passing a direct literal value.
    # This universally passes as 'production' is a valid literal in Mode.
    set_app_mode('production')

    # Case 2: Passing a variable whose type is inferred.
    # This is the intended point of divergence:
    # - Mypy and Pyright are known for strong literal inference. They are likely
    #   to infer `AppConfig.DEFAULT_MODE` as `Literal['production']`,
    #   which is compatible with `Mode`. This would lead to a PASS for them.
    # - Other type checkers (like Zuban or Ty) might be less aggressive
    #   with literal inference for untyped class attributes. They could
    #   potentially infer the type as `str`, which is not assignable to `Mode`.
    #   If they infer `str`, this would lead to an ERROR for them.
    set_app_mode(AppConfig.DEFAULT_MODE)

    # Case 3: Passing a string literal that is NOT in Mode.
    # This should universally fail for all type checkers.
    # set_app_mode('invalid_mode') # Uncomment to confirm this error


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(mode=...)
def test_set_app_mode(mode):
    """Property test: set_app_mode() with generated inputs."""
    result = set_app_mode(mode)


if __name__ == "__main__":
    test_set_app_mode()
