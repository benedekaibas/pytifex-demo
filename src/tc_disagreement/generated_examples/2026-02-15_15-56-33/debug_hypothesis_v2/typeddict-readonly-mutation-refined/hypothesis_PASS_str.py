"""Hypothesis Tier 2 test artifact.

Annotation: str
Variable: name
Resolved type: <class 'str'>
Status: PASS
"""

# --- Original source code (full context) ---
from typing import Protocol, List, TypedDict, runtime_checkable, Any
from typing_extensions import ReadOnly, NotRequired

# MODIFICATION: Configurable is now a TypedDict, not a Protocol.
# This change allows MyConfig to inherit from it directly, resolving the
# initial type checker error about TypedDict inheritance.
# This structure focuses the divergence on the interaction between
# ReadOnly fields in TypedDict inheritance and subsequent mutation.
class Configurable(TypedDict):
    name: str
    settings: List[str] # Expects a mutable list of settings

# MyConfig now explicitly inherits from Configurable (as a TypedDict).
# It overrides 'settings' to be ReadOnly, creating the core conflict.
class MyConfig(Configurable):
    settings: ReadOnly[List[str]] # Overrides 'settings' to be ReadOnly
    version: NotRequired[str]

# MODIFICATION: add_setting is now a standalone function.
# It expects an argument typed as the base 'Configurable' TypedDict.
def add_setting_func(cfg_dict: Configurable, setting_name: str) -> None:
    """Adds a setting to the list within the TypedDict."""
    # This line attempts to modify 'settings'.
    # If cfg_dict *actually* refers to an instance of MyConfig,
    # this mutation conflicts with MyConfig's ReadOnly[List[str]].
    cfg_dict['settings'].append(setting_name)

# The processing function now calls the standalone 'add_setting_func'.
def process_configurable(cfg: Configurable) -> None:
    """Processes a configurable object, calling its add_setting function."""
    print(f"Processing config: {cfg['name']}")
    # Call the standalone function, which attempts to modify 'settings'.
    # The divergence is expected here:
    # Will type checkers detect that `cfg` originating from `MyConfig`
    # means `cfg['settings']` is ReadOnly, despite `cfg` being typed as `Configurable`?
    add_setting_func(cfg, "new_feature")

if __name__ == "__main__":
    # 1. Test with a regular Configurable (mutable)
    # This TypedDict instance has mutable 'settings'.
    rc: Configurable = {"name": "System A", "settings": ["opt1"]}
    process_configurable(rc)
    print(f"RealConfig settings after processing: {rc['settings']}")
    # Expected: ['opt1', 'new_feature']

    # 2. Test with MyConfig (TypedDict with ReadOnly 'settings')
    # MyConfig correctly inherits from Configurable (both are TypedDicts).
    # The conflict is: MyConfig.settings is ReadOnly[List[str]], but
    # add_setting_func expects Configurable.settings (List[str]) and mutates it.
    mc: MyConfig = {"name": "System B", "settings": ["opt_A", "opt_B"]}

    # EXPECTED DIVERGENCE:
    # Some type checkers might allow this call because ReadOnly[T] is
    # assignable to T (for input positions), but then fail to catch the
    # mutation within add_setting_func due to type erasure or limited
    # flow analysis. Others might detect the implicit mutation intent
    # and flag the incompatibility earlier.
    process_configurable(mc)
    print(f"MyConfig settings after processing (should be unchanged): {mc['settings']}")
    # Expected runtime behavior: ['opt_A', 'opt_B', 'new_feature'] (mutation occurs)
    # Expected static type check behavior: error due to ReadOnly conflict.

# --- Hypothesis test ---
from hypothesis import given, settings, strategies as st
from typeguard import check_type, TypeCheckError

# To reproduce: run this file directly
# Annotation under test: str
# check_type(value, str)
