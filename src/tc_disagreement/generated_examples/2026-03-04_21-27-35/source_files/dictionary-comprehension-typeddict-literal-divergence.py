from typing import Literal, Union, TypedDict, Any
from typing_extensions import reveal_type

# Define TypedDicts for more precise initial typing
# This helps the type checker understand the possible values for each key.
class UserSettings(TypedDict):
    theme: str
    notifications: bool
    level: int

class AppSettings(TypedDict):
    version: str
    beta: bool
    mode: Literal["dev", "prod"]

class AdminSettings(TypedDict):
    privilege: str
    active: Literal[0, 1] # Using Literal here makes type inference more precise
    status: Literal["pending", "approved", "rejected"] # New key with Literal options

# A Union of all possible settings types for the values of the top-level 'configs' dictionary
ConfigType = Union[UserSettings, AppSettings, AdminSettings]

if __name__ == "__main__":
    # Annotate 'configs' with the precise type, leveraging TypedDicts
    configs: dict[str, ConfigType] = {
        "user_settings": {"theme": "dark", "notifications": True, "level": 10},
        "app_settings": {"version": "1.0", "beta": False, "mode": "prod"},
        "admin_settings": {"privilege": "full", "active": 1, "status": "pending"},
    }

    # Example 1: filter and transform dictionary values based on type
    # This original example showed divergence in the provided checker results,
    # as some checkers failed to infer the correct `Union[int, float]` type.
    # Using TypedDicts might influence how `outer_v.items()` are typed initially.
    filtered_numeric_values = {
        outer_k: [v for inner_k, v in outer_v.items() if isinstance(v, (int, float))]
        for outer_k, outer_v in configs.items()
    }
    # Expected type for filtered_numeric_values: dict[str, list[Union[int, float]]]
    reveal_type(filtered_numeric_values)

    # Example 2: comprehension that creates a dict of transformed values
    # This example is generally robust and less likely to diverge, as all values
    # are explicitly cast to string or replaced with string literals.
    processed_settings = {
        k: {
            inner_k: (
                "ON" if v is True else "OFF" if v is False else str(v)
            )
            for inner_k, v in inner_dict.items() if isinstance(v, (bool, int, str))
        }
        for k, inner_dict in configs.items()
    }
    # Expected: dict[str, dict[str, str]] (all values become strings)
    reveal_type(processed_settings)

    # Example 3: A comprehension using type narrowing to select specific keys and types.
    # This is the primary target for creating divergence.
    # The complexity arises from:
    # 1. Iterating `items()` of a `Union` of `TypedDict`s. The type of `v` before filtering is broad.
    # 2. The `if` condition combining `isinstance(v, bool)` with key-based filtering (`inner_k in ["active", "status"]`).
    # 3. How type checkers handle narrowing `v` based on `inner_k` when `outer_v` is a `TypedDict` (or a union of them),
    #    and specifically how `Literal` types (like `1` for `active` or `"pending"` for `status`) are preserved
    #    or widened to broader types (e.g., `int` or `str`).
    selected_complex_flags = {
        outer_k: {
            inner_k: reveal_type(v) # Reveal type of 'v' inside to see intermediate narrowing
            for inner_k, v in outer_v.items()
            if isinstance(v, bool) or inner_k in ["active", "status"]
        }
        for outer_k, outer_v in configs.items()
    }
    # Expected overall type for selected_complex_flags:
    # dict[str, dict[str, Union[bool, Literal[1], Literal["pending"]]]]
    #
    # Divergence is expected here:
    # - Some checkers might correctly infer `Literal[1]` and `Literal["pending"]`.
    # - Others might widen these to `int` and `str` respectively, resulting in
    #   `dict[str, dict[str, Union[bool, int, str]]]`.
    # - The `reveal_type(v)` inside the comprehension will show how `v` is typed after the filter.
    reveal_type(selected_complex_flags)