from typing import NewType, Union, TypeGuard
from typing_extensions import reveal_type

SensorReading = NewType("SensorReading", float)
DeviceId = NewType("DeviceId", int)
StatusCode = NewType("StatusCode", int)

MixedValues = Union[SensorReading, DeviceId, StatusCode, str, bool, float, int]

# This TypeGuard is designed to create divergence.
# It checks for base types (int, float) but promises to narrow to a Union
# that includes the NewType wrappers (SensorReading, DeviceId, StatusCode)
# along with raw int and float.
#
# Divergence is expected here because:
# - Mypy/Pyright: When `isinstance(val, (int, float))` is true, they typically
#   narrow `val` to its base type `int | float`, losing the `NewType` wrapper
#   information (DeviceId, StatusCode, SensorReading). Thus, `x` inside the
#   comprehension would be inferred as `int | float`.
# - Other checkers (e.g., Zuban, Pyrefly, Ty): Might respect the TypeGuard's
#   return annotation more literally, inferring `x` as the full promised type
#   `Union[SensorReading, DeviceId, StatusCode, float, int]`, even though the
#   runtime `isinstance` check doesn't preserve `NewType` distinctions.
def is_numeric_and_newtype_like(val: MixedValues) -> TypeGuard[Union[SensorReading, DeviceId, StatusCode, float, int]]:
    # At runtime, `isinstance(val, (int, float))` will be true for all
    # SensorReading, DeviceId, StatusCode instances (as they are just floats/ints),
    # as well as raw float and int values.
    # The ambiguity lies in how type checkers propagate the `NewType` information
    # through this TypeGuard when the runtime check is on the base type.
    return isinstance(val, (int, float))

if __name__ == "__main__":
    raw_data: list[MixedValues] = [
        SensorReading(10.5),
        DeviceId(101),
        "error",
        True,
        StatusCode(200),
        DeviceId(102),
        15.0, # raw float
        300,  # raw int
    ]

    # This comprehension applies the `is_numeric_and_newtype_like` TypeGuard.
    # The type revealed for `x` and the final `filtered_values_set` is the
    # expected point of divergence.
    filtered_values_set = {
        reveal_type(x) # EXPECTED DIVERGENCE:
                       # Mypy/Pyright might reveal: 'builtins.float | builtins.int'
                       # Others might reveal: 'Union[SensorReading, DeviceId, StatusCode, float, int]'
        for x in raw_data
        if is_numeric_and_newtype_like(x)
    }
    reveal_type(filtered_values_set) # EXPECTED DIVERGENCE:
                                     # Mypy/Pyright might reveal: 'set[builtins.float | builtins.int]'
                                     # Others might reveal: 'set[Union[SensorReading, DeviceId, StatusCode, float, int]]'