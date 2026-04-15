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