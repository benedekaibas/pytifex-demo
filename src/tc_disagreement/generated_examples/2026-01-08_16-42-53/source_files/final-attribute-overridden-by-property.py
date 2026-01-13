# id: final-attribute-overridden-by-property
# EXPECTED:
#   mypy: Error (Cannot override Final attribute with property)
#   pyright: No error
#   pyre: Error (Cannot override Final attribute with property)
#   zuban: Error (likely similar to Mypy/Pyre)
# REASON: Type checkers differ on whether a `Final` attribute in a base class can be "overridden"
#         by a `@property` with the same name in a derived class.
#         Mypy and Pyre strictly enforce the `Final` semantics, considering a `@property`
#         with the same name as an attempt to re-assign or redefine the final attribute,
#         even though properties have different access semantics.
#         Pyright is more lenient, potentially viewing the `@property` as a distinct
#         member or allowing it if it doesn't conflict with direct access semantics,
#         or if it represents a different kind of "override."

from typing import Final

class ServiceConfig:
    VERSION: Final[str] = "1.0.0"
    PORT: Final[int] = 8080

class DevServiceConfig(ServiceConfig):
    @property
    def PORT(self) -> int: # Mypy/Pyre might error here
        return 9000

if __name__ == "__main__":
    dev_config = DevServiceConfig()
    print(f"Dev service version: {dev_config.VERSION}")
    print(f"Dev service port: {dev_config.PORT}")
    # mypy: Cannot override Final attribute "PORT" with a property in class "DevServiceConfig" [misc]
    # pyright: No error
    # pyre: Inconsistent override [1]: `PORT` in `DevServiceConfig` is not a consistent override of `PORT` in `ServiceConfig`