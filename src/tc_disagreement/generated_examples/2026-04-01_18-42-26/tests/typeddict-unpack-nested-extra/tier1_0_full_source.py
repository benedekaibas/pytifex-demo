from typing import TypedDict, Unpack, Any

class MetadataDict(TypedDict, extra_items=str):
    created_by: str

class ReportConfig(TypedDict):
    report_name: str
    metadata: MetadataDict
    version: str

def generate_report(**kwargs: Unpack[ReportConfig]) -> None:
    print("Generating report with config:")
    print(f"  Name: {kwargs['report_name']}")
    print(f"  Version: {kwargs['version']}")
    print(f"  Metadata: {kwargs['metadata']}")
    if 'extra_config' in kwargs:
        print(f"  Extra Config: {kwargs['extra_config']}") # This should ideally be allowed

if __name__ == "__main__":
    # ReportConfig expects 'report_name', 'metadata' (which has extra_items), and 'version'.
    # When `ReportConfig` is unpacked, how do checkers handle the `extra_items`
    # property of a *nested* TypedDict?
    # This could lead to false positives/negatives if the checker
    # expects MetadataDict to not have 'additional_info'.

    # This should be allowed.
    generate_report(
        report_name="SalesOverview",
        version="1.0",
        metadata={
            "created_by": "admin",
            "last_modified": "2023-10-26" # This is an extra item for MetadataDict
        }
    )

    # What if ReportConfig itself had extra_items? Not the primary test here.
    # The key is `metadata` containing extra_items.
    # Some checkers might complain about 'additional_info' when unpacking.
    print("\nCalling with nested extra item:")
    generate_report(
        report_name="MonthlySummary",
        version="2.1",
        metadata={
            "created_by": "system",
            "additional_info": "daily-cron", # extra item in metadata
            "run_id": "abc1234" # another extra item
        }
    )