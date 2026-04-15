from typing import TypedDict, Required, NotRequired, TYPE_CHECKING, Literal, Optional, Union

# Robust reveal_type for different type checkers
# Some type checkers (like mypy, pyright) handle reveal_type as a special form
# within TYPE_CHECKING. Others (like pyrefly, ty in the initial test) might
# try to resolve it at runtime, leading to errors.
if TYPE_CHECKING:
    from typing_extensions import reveal_type as _reveal_type_ # Use an alias to avoid potential conflicts
else:
    def _reveal_type_(*args, **kwargs):
        pass # No-op at runtime

class BaseConfig(TypedDict): # total=True by default
    host: str
    port: int

class OptionalFeatures(TypedDict, total=False):
    # These fields are implicitly NotRequired due to total=False
    debug_mode: bool
    log_level: Literal["INFO", "WARN", "ERROR"]
    # This field is explicitly NotRequired
    telemetry_endpoint: NotRequired[str]

class FullServiceConfig(BaseConfig, OptionalFeatures, total=True): # Override to total=True
    # api_key is Required by default in a total=True TypedDict
    api_key: str
    # timeout_seconds explicitly NotRequired, even though FullServiceConfig is total=True
    timeout_seconds: NotRequired[int] 
    
    # What about 'debug_mode' and 'log_level' from OptionalFeatures?
    # They were implicitly NotRequired from OptionalFeatures(total=False).
    # If FullServiceConfig is total=True, do they become Required here?
    #
    # This is the core divergence point:
    # - Mypy (modern versions) typically makes them Required in FullServiceConfig,
    #   because `total=True` promotes implicitly NotRequired fields.
    # - Other checkers might allow their NotRequired status (from total=False parent)
    #   to persist, making them optional.
    # Explicitly NotRequired fields (like 'telemetry_endpoint' from OptionalFeatures,
    # or 'timeout_seconds' defined here) are expected to remain optional.

def validate_config(config: FullServiceConfig):
    if TYPE_CHECKING:
        _reveal_type_(config["host"]) # Expected str (from BaseConfig, required)
        _reveal_type_(config["api_key"]) # Expected str (from FullServiceConfig, required)

        # For 'debug_mode' and 'log_level':
        # Mypy 1.9.0+ will reveal these as 'bool' and 'Literal', implying they are Required.
        # This will lead to errors later if they are missing in a dict literal.
        _reveal_type_(config["debug_mode"]) # Mypy: 'bool'. Other checkers might report 'Optional[bool]' or error if accessed without 'in' check.
        _reveal_type_(config["log_level"]) # Mypy: 'Literal'. Other checkers might report 'Optional[Literal]'.
        
        # When accessing potentially optional fields, .get() is safer and shows Optional type
        _reveal_type_(config.get("debug_mode")) # Expected Union[bool, None] if optional. Mypy: Union[bool, None]
        _reveal_type_(config.get("log_level")) # Expected Union[Literal, None] if optional. Mypy: Union[Literal, None]

        # Explicitly NotRequired fields should consistently be Optional
        _reveal_type_(config.get("timeout_seconds")) # Expected Union[int, None] (universally agreed)
        _reveal_type_(config.get("telemetry_endpoint")) # Expected Union[str, None] (universally agreed for explicit NotRequired)

    print(f"Host: {config['host']}, API Key: {config['api_key']}")
    if "debug_mode" in config:
        print(f"Debug Mode: {config['debug_mode']}")
    if "log_level" in config:
        print(f"Log Level: {config['log_level']}")
    if "timeout_seconds" in config:
        print(f"Timeout: {config['timeout_seconds']}")
    if "telemetry_endpoint" in config:
        print(f"Telemetry: {config['telemetry_endpoint']}")

if __name__ == "__main__":
    # --- Config 1: Missing 'debug_mode' and 'log_level' ---
    # Mypy 1.9.0+ will flag this as an error because 'FullServiceConfig' is total=True,
    # making 'debug_mode' and 'log_level' required.
    # Other checkers might allow it, deferring to OptionalFeatures' total=False.
    cfg1: FullServiceConfig = {
        "host": "localhost",
        "port": 8080,
        "api_key": "secret-key-123",
        "timeout_seconds": 60 # This field is NotRequired, so its presence/absence is fine
    }
    print("--- Config 1 (missing debug_mode, log_level) ---")
    validate_config(cfg1)

    # --- Config 2: Full configuration ---
    # This configuration should be valid for all checkers.
    cfg2: FullServiceConfig = {
        "host": "remote.server",
        "port": 443,
        "api_key": "secret-key-456",
        "debug_mode": True,
        "log_level": "INFO", # Corrected from "DEBUG" to match Literal
        "telemetry_endpoint": "http://telemetry.com"
    }
    print("\n--- Config 2 (full) ---")
    validate_config(cfg2)

    # --- Config 3: Partially missing optional fields ---
    # Mypy 1.9.0+ will flag this as an error because 'debug_mode' is missing.
    # Other checkers might allow it.
    cfg3: FullServiceConfig = {
        "host": "another.server",
        "port": 80,
        "api_key": "secret-key-789",
        "log_level": "WARN", # 'log_level' is present
        # 'debug_mode' is missing here
    }
    print("\n--- Config 3 (only log_level present) ---")
    validate_config(cfg3)