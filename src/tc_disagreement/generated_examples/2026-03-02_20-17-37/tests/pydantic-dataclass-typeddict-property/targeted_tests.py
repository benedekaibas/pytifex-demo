"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: pydantic-dataclass-typeddict-property.py
Patterns detected: 1
    - decorator_signature (4 tests)
Test cases generated: 4
"""

# --- Original source ---

import pydantic
import typing as t
from typing import TypedDict, Union, Literal

class Metadata(TypedDict, total=False):
    tags: t.List[str]
    source: str
    version: t.Optional[str] # Optional field

class ExtendedInfo(TypedDict):
    owner: str
    last_modified: str

@pydantic.dataclasses.dataclass(frozen=True)
class DataRecord:
    record_id: str
    value: int
    metadata: Metadata
    extended_info: Union[ExtendedInfo, Literal["not_available"]] # Union for complexity

    @property
    def record_tags(self) -> t.List[str]:
        # Accessing TypedDict fields via property, especially an optional one like 'tags'
        # Type checkers might struggle with the TypedDict field access combined with Pydantic.
        return self.metadata.get('tags', []) # 'tags' might be missing if not_available (total=False)

    @property
    def owner_email(self) -> t.Optional[str]:
        # Accessing TypedDict fields in a union, post-narrowing
        if self.extended_info == "not_available":
            return None
        reveal_type(self.extended_info) # Expected: ExtendedInfo
        # 'owner' is a required field within ExtendedInfo
        return f"{self.extended_info['owner']}@example.com"

if __name__ == '__main__':
    record_full = DataRecord(
        record_id="REC-001",
        value=100,
        metadata=Metadata(tags=["alpha", "beta"], source="sensor"),
        extended_info=ExtendedInfo(owner="Alice", last_modified="2023-01-01")
    )
    print(f"Record {record_full.record_id}: Tags={record_full.record_tags}, Owner Email={record_full.owner_email}")

    record_partial = DataRecord(
        record_id="REC-002",
        value=200,
        metadata=Metadata(source="manual"), # 'tags' missing (total=False)
        extended_info=ExtendedInfo(owner="Bob", last_modified="2023-02-01")
    )
    print(f"Record {record_partial.record_id}: Tags={record_partial.record_tags}, Owner Email={record_partial.owner_email}")

    record_no_extended_info = DataRecord(
        record_id="REC-003",
        value=300,
        metadata=Metadata(tags=["gamma"], source="system"),
        extended_info="not_available"
    )
    print(f"Record {record_no_extended_info.record_id}: Tags={record_no_extended_info.record_tags}, Owner Email={record_no_extended_info.owner_email}")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_DataRecord_record_tags_decorated_callable():
    """Verify decorated method DataRecord.record_tags is callable."""
    try:
        obj = DataRecord()
        method = getattr(obj, "record_tags", None)
        if method is None:
            BUGS.append({"line": 22, "type": "AttributeError", "error": "DataRecord has no method record_tags after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 22, "type": "TypeError", "error": "DataRecord.record_tags is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 22, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_DataRecord_record_tags_no_args():
    """Call decorated DataRecord.record_tags with no extra args."""
    try:
        obj = DataRecord()
        result = obj.record_tags()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 22, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_DataRecord_owner_email_decorated_callable():
    """Verify decorated method DataRecord.owner_email is callable."""
    try:
        obj = DataRecord()
        method = getattr(obj, "owner_email", None)
        if method is None:
            BUGS.append({"line": 28, "type": "AttributeError", "error": "DataRecord has no method owner_email after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 28, "type": "TypeError", "error": "DataRecord.owner_email is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 28, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_DataRecord_owner_email_no_args():
    """Call decorated DataRecord.owner_email with no extra args."""
    try:
        obj = DataRecord()
        result = obj.owner_email()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 28, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
