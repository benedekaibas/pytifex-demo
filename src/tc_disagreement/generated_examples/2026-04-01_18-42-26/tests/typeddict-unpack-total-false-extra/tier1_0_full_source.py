from typing import TypedDict, Unpack, Any

class BaseSettings(TypedDict, total=False):
    debug: bool
    log_level: str

class AdvancedSettings(BaseSettings, extra_items=Any):
    timeout: int
    retries: int = 3 # Default value on field, not on type def

def apply_settings(**kwargs: Unpack[AdvancedSettings]) -> None:
    print("Applying settings:")
    for k, v in kwargs.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    # AdvancedSettings allows 'debug', 'log_level' (optional), 'timeout', 'retries' (required),
    # and any extra_items.
    # The combination of total=False, extra_items, and Unpack for kwargs is tricky.
    
    # This should be allowed.
    apply_settings(timeout=10, retries=5, debug=True, custom_flag=True, version="1.0")

    # What if 'retries' is missing? AdvancedSettings doesn't specify total=False.
    # TypedDicts are 'total=True' by default, and `total=False` does not propagate.
    # So 'timeout' and 'retries' should be required.
    # apply_settings(timeout=10, debug=True, custom_flag=True) # This should error for 'retries'
    
    # If a checker correctly infers that `retries` is Required, this should fail.
    # If it over-applies total=False from BaseSettings, it might allow it.
    print("\nAttempting call with missing required field (should error):")
    try:
        # Example that should produce an error for missing 'retries'
        # based on AdvancedSettings inheriting total=True behavior by default
        # for its own fields and overriding total=False from BaseSettings.
        # Pyright (original issue) specifically struggled with extra_items and Unpack.
        apply_settings(timeout=10, debug=True, extra_val="foo")
    except TypeError as e:
        print(f"Caught expected runtime error: {e}")
    except Exception:
        print("Type checker should have caught this prior to runtime.")